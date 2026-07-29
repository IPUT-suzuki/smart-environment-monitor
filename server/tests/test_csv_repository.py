import csv
import multiprocessing
import tempfile
import unittest
from pathlib import Path

from common.csv_schema import SENSOR_CSV_FIELDS
from server.repositories.csv_sensor_repository import CsvSensorRepository


def payload(client_id: str, session_id: str, sequence: int):
    return {
        "client_id": client_id,
        "region": "test",
        "datetime": f"2026-07-29 10:00:{sequence:02d}",
        "session_id": session_id,
        "sequence": sequence,
        "sensor_data": {"temperature": 20.0 + sequence, "humidity": 50.0, "pressure": 1000.0, "co2": 500},
    }


def save_from_receiver(path_string: str, sequence: int):
    CsvSensorRepository(Path(path_string)).save(payload("receiver", "receiver-session", sequence))


def save_from_web(path_string: str, temperature: float):
    from web import app as web_app

    web_app.CSV_CANDIDATES = [Path(path_string)]
    web_app.append_manual_sensor_rows([{
        "temperature": temperature,
        "humidity": 50.0,
        "pressure": 1000.0,
        "co2": 700,
    }])


class CsvSensorRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "sensor_data.csv"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_deduplicates_across_repository_instances(self):
        first = CsvSensorRepository(self.path)
        second = CsvSensorRepository(self.path)

        self.assertFalse(first.save(payload("client-a", "session-a", 1)).duplicate)
        result = second.save(payload("client-a", "session-a", 1))

        self.assertTrue(result.duplicate)
        self.assertEqual(second.total_rows(), 1)

    def test_receiver_and_web_writes_do_not_corrupt_csv_across_processes(self):
        context = multiprocessing.get_context("spawn")
        processes = [
            context.Process(target=save_from_receiver, args=(str(self.path), sequence))
            for sequence in range(1, 5)
        ] + [
            context.Process(target=save_from_web, args=(str(self.path), temperature))
            for temperature in (31.0, 32.0)
        ]
        for process in processes:
            process.start()
        for process in processes:
            process.join(15)
            self.assertEqual(process.exitcode, 0)

        with self.path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            self.assertEqual(reader.fieldnames, list(SENSOR_CSV_FIELDS))
            rows = list(reader)
        self.assertEqual(len(rows), 6)
        self.assertEqual({row["client_id"] for row in rows}, {"receiver", "web-manual"})
        self.assertTrue(all(set(SENSOR_CSV_FIELDS).issubset(row) for row in rows))
