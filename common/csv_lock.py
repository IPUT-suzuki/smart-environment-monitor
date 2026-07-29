"""Cross-platform, process-safe locking for small CSV files.

The lock is an atomically-created sibling directory (``<csv>.lock``), so it
works with the Python standard library on both Windows and POSIX platforms.
It intentionally does not use ``fcntl``.  A stale empty lock directory is
removed after a configurable age, which lets a later process recover after an
unexpected termination.
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class CsvLockTimeoutError(TimeoutError):
    """Raised when a CSV lock cannot be acquired before its deadline."""


@contextmanager
def csv_lock(
    csv_path: Path,
    *,
    timeout_seconds: float = 5.0,
    stale_after_seconds: float = 60.0,
    retry_interval_seconds: float = 0.05,
) -> Iterator[None]:
    """Acquire a process-safe lock associated with *csv_path*.

    CSV operations in this project are short.  The stale-lock recovery window
    is therefore deliberately much longer than a normal write, avoiding a
    competing writer while still recovering from a process that was killed.
    """

    lock_path = Path(f"{csv_path}.lock")
    deadline = time.monotonic() + timeout_seconds
    acquired = False
    while not acquired:
        try:
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            os.mkdir(lock_path)
            acquired = True
        except FileExistsError:
            try:
                age_seconds = time.time() - lock_path.stat().st_mtime
                if age_seconds >= stale_after_seconds:
                    os.rmdir(lock_path)
                    continue
            except (FileNotFoundError, OSError):
                # Another process released or is handling the lock; retry.
                continue
            if time.monotonic() >= deadline:
                raise CsvLockTimeoutError(f"timed out waiting for CSV lock: {lock_path}")
            time.sleep(retry_interval_seconds)
    try:
        yield
    finally:
        if acquired:
            try:
                os.rmdir(lock_path)
            except FileNotFoundError:
                pass
