import csv
import logging
import threading
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


CSV_FIELDS = [
    "client_id", "region", "datetime", "session_id", "sequence",
    "temperature", "humidity", "pressure", "co2",
]

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SaveResult:
    received_count: int
    duplicate: bool


class CsvSensorRepository:
    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.Lock()
        self._counts: Counter[str] = Counter()
        self._seen: set[tuple[str, str, int]] = set()
        self._ensure_storage()
        self._load_state()

    def _ensure_storage(self) -> None:
        """Create the data directory and an empty CSV with its header once."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            return
        with self.path.open("x", newline="", encoding="utf-8") as file:
            csv.DictWriter(file, fieldnames=CSV_FIELDS).writeheader()
        logger.info("created sensor data file: %s", self.path)

    def _load_state(self) -> None:
        if not self.path.exists():
            return
        with self.path.open("r", newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                client_id = row.get("client_id")
                if not client_id:
                    continue
                self._counts[client_id] += 1
                try:
                    sequence = int(row.get("sequence", ""))
                    session_id = row.get("session_id", "")
                except ValueError:
                    continue
                if session_id and sequence > 0:
                    self._seen.add((client_id, session_id, sequence))

    def _migrate_schema(self) -> None:
        if not self.path.exists():
            return
        with self.path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames == CSV_FIELDS:
                return
            rows = list(reader)
        migrating = self.path.with_suffix(".migrating")
        with migrating.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
            writer.writeheader()
            for old_row in rows:
                writer.writerow({field: old_row.get(field, "") for field in CSV_FIELDS})
        migrating.replace(self.path)

    def save(self, payload: dict) -> SaveResult:
        client_id = payload["client_id"]
        key = (client_id, payload["session_id"], payload["sequence"])
        with self._lock:
            if key in self._seen:
                return SaveResult(self._counts[client_id], True)
            self._migrate_schema()
            sensor_data = payload["sensor_data"]
            row = {
                "client_id": client_id,
                "region": payload["region"],
                "datetime": payload["datetime"],
                "session_id": payload["session_id"],
                "sequence": payload["sequence"],
                **sensor_data,
            }
            file_exists = self.path.exists()
            with self.path.open("a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row)
            self._seen.add(key)
            self._counts[client_id] += 1
            return SaveResult(self._counts[client_id], False)

    def total_rows(self) -> int:
        with self._lock:
            return sum(self._counts.values())
