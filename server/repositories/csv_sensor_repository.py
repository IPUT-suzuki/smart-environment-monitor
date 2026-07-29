"""Process-safe persistence for sensor measurements."""

from __future__ import annotations

import csv
import logging
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from common.csv_lock import csv_lock
from common.csv_schema import SENSOR_CSV_FIELDS
from server.config.settings import CSV_LOCK_STALE_AFTER_SECONDS, CSV_LOCK_TIMEOUT_SECONDS


CSV_FIELDS = list(SENSOR_CSV_FIELDS)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SaveResult:
    received_count: int
    duplicate: bool


class CsvSensorRepository:
    """Store complete TCP payloads while coordinating with the Web process.

    State is refreshed while holding the shared CSV lock before every save.
    This keeps deduplication and per-client acknowledgement counts correct even
    when receiver processes are restarted or a manual Web write happened.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self._counts: Counter[str] = Counter()
        self._seen: set[tuple[str, str, int]] = set()
        self._ensure_storage()
        with self._locked_csv():
            self._migrate_schema_unlocked()
            self._refresh_state_unlocked()

    def _locked_csv(self):
        return csv_lock(
            self.path,
            timeout_seconds=CSV_LOCK_TIMEOUT_SECONDS,
            stale_after_seconds=CSV_LOCK_STALE_AFTER_SECONDS,
        )

    def _ensure_storage(self) -> None:
        with self._locked_csv():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if self.path.exists():
                return
            with self.path.open("w", newline="", encoding="utf-8") as file:
                csv.DictWriter(file, fieldnames=CSV_FIELDS).writeheader()
                file.flush()
                os.fsync(file.fileno())
            logger.info("created sensor data file: %s", self.path)

    def _read_rows_unlocked(self) -> tuple[list[str], list[dict[str, str]]]:
        if not self.path.exists():
            return [], []
        with self.path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            return list(reader.fieldnames or []), list(reader)

    def _refresh_state_unlocked(self) -> None:
        self._counts.clear()
        self._seen.clear()
        _, rows = self._read_rows_unlocked()
        for row in rows:
            client_id = row.get("client_id", "")
            if not client_id:
                continue
            self._counts[client_id] += 1
            try:
                sequence = int(row.get("sequence", ""))
            except (TypeError, ValueError):
                continue
            session_id = row.get("session_id", "")
            if session_id and sequence > 0:
                self._seen.add((client_id, session_id, sequence))

    def _migrate_schema_unlocked(self) -> None:
        """Migrate a legacy schema atomically while no reader can see it."""
        fieldnames, rows = self._read_rows_unlocked()
        if not fieldnames or fieldnames == CSV_FIELDS:
            return
        migrating = self.path.with_name(f"{self.path.name}.{os.getpid()}.migrating")
        with migrating.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows({field: row.get(field, "") for field in CSV_FIELDS} for row in rows)
            file.flush()
            os.fsync(file.fileno())
        os.replace(migrating, self.path)
        logger.info("migrated sensor CSV schema: %s", self.path)

    def save(self, payload: dict) -> SaveResult:
        client_id = payload["client_id"]
        key = (client_id, payload["session_id"], payload["sequence"])
        with self._locked_csv():
            self._ensure_storage_unlocked()
            self._migrate_schema_unlocked()
            self._refresh_state_unlocked()
            if key in self._seen:
                return SaveResult(self._counts[client_id], True)

            row = {
                "client_id": client_id,
                "region": payload["region"],
                "datetime": payload["datetime"],
                "session_id": payload["session_id"],
                "sequence": payload["sequence"],
                **payload["sensor_data"],
            }
            with self.path.open("a", newline="", encoding="utf-8") as file:
                csv.DictWriter(file, fieldnames=CSV_FIELDS).writerow(row)
                file.flush()
                os.fsync(file.fileno())
            self._seen.add(key)
            self._counts[client_id] += 1
            return SaveResult(self._counts[client_id], False)

    def _ensure_storage_unlocked(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            return
        with self.path.open("w", newline="", encoding="utf-8") as file:
            csv.DictWriter(file, fieldnames=CSV_FIELDS).writeheader()
            file.flush()
            os.fsync(file.fileno())

    def total_rows(self) -> int:
        with self._locked_csv():
            self._ensure_storage_unlocked()
            self._migrate_schema_unlocked()
            self._refresh_state_unlocked()
            return sum(self._counts.values())
