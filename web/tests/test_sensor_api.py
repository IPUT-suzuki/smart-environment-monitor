import csv
import re
import tempfile
import unittest
from pathlib import Path

from web import app as web_app


SENSOR_FIELDS = [
    "client_id", "region", "datetime", "session_id", "sequence",
    "temperature", "humidity", "pressure", "co2",
]


def manual_row(**overrides):
    row = {
        "temperature": 25.0,
        "humidity": 50.0,
        "pressure": 1000.0,
        "co2": 700,
    }
    row.update(overrides)
    return row


class SensorApiTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.original_candidates = web_app.CSV_CANDIDATES
        self.csv_path = Path(self.temp_dir.name) / "sensor_data.csv"
        web_app.CSV_CANDIDATES = [self.csv_path]
        with self.csv_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=SENSOR_FIELDS)
            writer.writeheader()
            writer.writerows([
                {
                    "client_id": "TK-002", "region": "osaka", "datetime": "2026-06-22 Monday 10:00:00",
                    "session_id": "session-b", "sequence": "2", "temperature": "25.0", "humidity": "50.0", "pressure": "1005.0", "co2": "700",
                },
                {
                    "client_id": "TK-001", "region": "tokyo", "datetime": "2026-06-22 Monday 09:00:00",
                    "session_id": "session-a", "sequence": "1", "temperature": "21.0", "humidity": "40.0", "pressure": "1000.0", "co2": "500",
                },
                {
                    "client_id": "TK-001", "region": "tokyo", "datetime": "2026-06-22 Monday 11:00:00",
                    "session_id": "session-a", "sequence": "3", "temperature": "30.0", "humidity": "60.0", "pressure": "1010.0", "co2": "900",
                },
            ])
        self.client = web_app.app.test_client()

    def tearDown(self):
        web_app.CSV_CANDIDATES = self.original_candidates
        self.temp_dir.cleanup()

    def test_sensor_data_returns_json_response_shape(self):
        response = self.client.get("/api/sensor-data")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        payload = response.get_json()
        self.assertEqual(payload["row_count"], 3)
        self.assertEqual([row["sequence"] for row in payload["rows"]], ["3", "2", "1"])
        self.assertEqual(list(payload["field_labels"]), SENSOR_FIELDS)
        self.assertEqual(payload["field_labels"]["temperature"], "温度")

    def test_search_filters_and_returns_actual_json_response(self):
        response = self.client.get(
            "/api/sensor-data/search",
            query_string={
                "client_id": "TK-001",
                "client_id_match": "equals",
                "datetime_from": "2026-06-22T10:00:00+09:00",
                "temperature_min": "25",
                "co2_max": "900",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        payload = response.get_json()
        self.assertEqual(payload["row_count"], 1)
        self.assertEqual(payload["rows"][0]["sequence"], "3")
        self.assertEqual(payload["filters"]["client_id"], {"value": "TK-001", "match": "equals"})
        self.assertEqual(payload["filters"]["temperature"]["min"], 25.0)

    def test_search_rejects_invalid_query(self):
        response = self.client.get("/api/sensor-data/search?humidity_min=high")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.mimetype, "application/json")
        self.assertIn("error", response.get_json())

    def test_api_docs_page_contains_request_controls(self):
        response = self.client.get("/api/docs")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"api-reference", response.data)
        self.assertIn(b"/api/sensor-data/search", response.data)
        self.assertIn(b"/api/sensor-data/download", response.data)
        self.assertIn(b"/api/sensor-data/manual", response.data)
        self.assertIn(b"/api/health/&lt;client_id&gt;/download", response.data)
        self.assertIn(b"data-api-search-form", response.data)
        self.assertIn(b"data-api-body-target", response.data)
        self.assertIn(b"data-health-download-form", response.data)
        self.assertIn(b"data-health-stream-start", response.data)
        self.assertIn(b"api-toc", response.data)
        self.assertIn(b"data-copy-api-url", response.data)
        self.assertIn(b"data-api-result", response.data)
        self.assertIn(b'id="health-post"', response.data)
        self.assertEqual(response.data.count(b"data-api-write-toggle>"), 2)
        self.assertEqual(response.data.count(b'data-safe-label="'), 2)
        self.assertIn(b"rows[].temperature", response.data)
        self.assertIn(b"rows[].humidity", response.data)

    def test_api_markdown_documents_every_operation(self):
        api_document = (
            Path(web_app.__file__).resolve().parent / "docs" / "api.md"
        ).read_text(encoding="utf-8")

        expected_operations = (
            "GET `/api/sensor-data`",
            "GET `/api/sensor-data/search`",
            "GET `/api/sensor-data/download`",
            "POST `/api/sensor-data/manual`",
            "GET `/api/health`",
            "POST `/api/health`",
            "GET `/api/health/<client_id>/download`",
            "GET `/api/health/stream`",
        )
        for operation in expected_operations:
            with self.subTest(operation=operation):
                self.assertIn(operation, api_document)
        self.assertIn("認証とTLSは実装されていません", api_document)
        self.assertIn("HEALTH_STREAM_KEEPALIVE_SECONDS", api_document)
        self.assertIn("`dry_run=true`", api_document)

    def test_api_parameter_tables_do_not_overflow_the_console(self):
        api_styles = (
            Path(web_app.__file__).resolve().parent / "static" / "api-reference.css"
        ).read_text(encoding="utf-8")

        self.assertIn("table-layout: fixed;", api_styles)
        self.assertIn("overflow-wrap: anywhere;", api_styles)

    def test_dashboard_has_sensor_csv_download_button_and_average_summary(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"data-csv-download", response.data)
        self.assertIn(b'data-average="temperature"', response.data)

    def test_sensor_empty_state_has_a_dedicated_selector(self):
        response = self.client.get("/")
        script = (Path(web_app.__file__).resolve().parent / "static" / "app.js").read_text(encoding="utf-8")

        self.assertIn(b"data-sensor-empty", response.data)
        self.assertIn('document.querySelector("[data-sensor-empty]")', script)
        self.assertNotIn('document.querySelector(".empty-state")', script)

    def test_average_summary_is_scoped_to_data_and_graph_views(self):
        response = self.client.get("/")
        script = (Path(web_app.__file__).resolve().parent / "static" / "app.js").read_text(encoding="utf-8")

        self.assertIn(b"data-average-summary", response.data)
        self.assertIn('averageSummary.hidden = !["table", "graph"].includes(view);', script)

    def test_dashboard_contains_health_detail_modal(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"data-health-modal", response.data)
        self.assertIn(b"data-health-modal-details", response.data)
        self.assertIn(b'aria-labelledby="health-modal-title"', response.data)

    def test_manual_single_row(self):
        response = self.client.post(
            "/api/sensor-data/manual",
            json={"rows": [manual_row()]},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        payload = response.get_json()
        self.assertEqual(payload["rows_added"], 1)

        with self.csv_path.open("r", encoding="utf-8") as csv_file:
            rows = list(csv.DictReader(csv_file))
        self.assertEqual(len(rows), 4)

        new_row = rows[-1]
        self.assertEqual(new_row["client_id"], "web-manual")
        self.assertEqual(new_row["region"], "web-input")
        self.assertEqual(new_row["sequence"], "1")
        self.assertRegex(
            new_row["datetime"],
            r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
        )
        self.assertEqual(new_row["co2"], "700")
        self.assertEqual(new_row["temperature"], "25.0")
        self.assertEqual(new_row["humidity"], "50.0")
        self.assertEqual(new_row["pressure"], "1000.0")

    def test_manual_dry_run_validates_without_writing(self):
        response = self.client.post(
            "/api/sensor-data/manual?dry_run=true",
            json={"rows": [manual_row()]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "valid": True,
            "dry_run": True,
            "rows_validated": 1,
        })
        with self.csv_path.open("r", encoding="utf-8") as csv_file:
            rows = list(csv.DictReader(csv_file))
        self.assertEqual(len(rows), 3)

    def test_invalid_dry_run_never_writes(self):
        response = self.client.post(
            "/api/sensor-data/manual?dry_run=maybe",
            json={"rows": [manual_row()]},
        )

        self.assertEqual(response.status_code, 400)
        with self.csv_path.open("r", encoding="utf-8") as csv_file:
            rows = list(csv.DictReader(csv_file))
        self.assertEqual(len(rows), 3)

    def test_dashboard_manual_input_uses_real_registration_endpoint(self):
        dashboard_script = (
            Path(web_app.__file__).resolve().parent / "static" / "app.js"
        ).read_text(encoding="utf-8")

        self.assertIn('fetch("/api/sensor-data/manual"', dashboard_script)
        self.assertNotIn("/api/sensor-data/manual?dry_run", dashboard_script)

    def test_manual_multi_row(self):
        response = self.client.post(
            "/api/sensor-data/manual",
            json={"rows": [
                {"temperature": 25.0, "humidity": 50.0, "pressure": 1000.0, "co2": 700},
                {"temperature": 26.0, "humidity": 55.0, "pressure": 1001.0, "co2": 750},
                {"temperature": 27.0, "humidity": 60.0, "pressure": 1002.0, "co2": 800},
            ]},
        )

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertEqual(payload["rows_added"], 3)

        with self.csv_path.open("r", encoding="utf-8") as csv_file:
            rows = list(csv.DictReader(csv_file))
        new_rows = rows[-3:]
        self.assertEqual([r["sequence"] for r in new_rows], ["1", "2", "3"])
        session_ids = {r["session_id"] for r in new_rows}
        self.assertEqual(len(session_ids), 1)

    def test_manual_invalid_temperature(self):
        response = self.client.post(
            "/api/sensor-data/manual",
            json={"rows": [
                {"temperature": "not-a-number", "humidity": 50.0, "pressure": 1000.0, "co2": 700},
            ]},
        )

        self.assertEqual(response.status_code, 400)
        with self.csv_path.open("r", encoding="utf-8") as csv_file:
            row_count = sum(1 for _ in csv.DictReader(csv_file))
        self.assertEqual(row_count, 3)

    def test_manual_rejects_incomplete_sensor_snapshot(self):
        response = self.client.post(
            "/api/sensor-data/manual",
            json={"rows": [{"temperature": 25.0}]},
        )

        self.assertEqual(response.status_code, 400)
        with self.csv_path.open("r", encoding="utf-8") as csv_file:
            rows = list(csv.DictReader(csv_file))
        self.assertEqual(len(rows), 3)

    def test_manual_rejects_non_finite_numbers(self):
        for field in ("temperature", "humidity", "pressure", "co2"):
            for value in (float("nan"), float("inf"), float("-inf")):
                with self.subTest(field=field, value=value):
                    response = self.client.post(
                        "/api/sensor-data/manual",
                        json={"rows": [manual_row(**{field: value})]},
                    )
                    self.assertEqual(response.status_code, 400)

    def test_manual_rejects_sensor_values_with_wrong_precision(self):
        invalid_values = {
            "temperature": 25.12,
            "humidity": 50.12,
            "pressure": 1000.12,
            "co2": 700.5,
        }
        for field, value in invalid_values.items():
            with self.subTest(field=field):
                response = self.client.post(
                    "/api/sensor-data/manual",
                    json={"rows": [manual_row(**{field: value})]},
                )
                self.assertEqual(response.status_code, 400)

    def test_manual_rejects_unknown_measurement_field(self):
        response = self.client.post(
            "/api/sensor-data/manual",
            json={"rows": [manual_row(voltage=3.3)]},
        )

        self.assertEqual(response.status_code, 400)

    def test_sensor_csv_download_uses_filters_sort_and_utf8_bom(self):
        response = self.client.get(
            "/api/sensor-data/download",
            query_string={
                "client_id": "TK-001",
                "client_id_match": "equals",
                "temperature_min": "25",
                "sort_by": "temperature",
                "sort_order": "asc",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/csv")
        self.assertTrue(response.data.startswith(b"\xef\xbb\xbf"))
        rows = list(csv.DictReader(response.data.decode("utf-8-sig").splitlines()))
        self.assertEqual([row["sequence"] for row in rows], ["3"])
        self.assertRegex(response.headers["Content-Disposition"], r'sensor-data-\d{8}-\d{6}\.csv')

    def test_sensor_csv_download_returns_header_for_no_matches(self):
        response = self.client.get("/api/sensor-data/download?client_id=missing&client_id_match=equals")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.startswith(b"\xef\xbb\xbfclient_id,region,"))
        self.assertEqual(len(response.data.decode("utf-8-sig").splitlines()), 1)

    def test_averages_ignore_blank_and_invalid_values(self):
        rows = [
            {"temperature": "10", "humidity": "", "pressure": "1000", "co2": "400"},
            {"temperature": "20", "humidity": "NaN", "pressure": "", "co2": "600"},
            {"temperature": "invalid", "humidity": "50", "pressure": "1010", "co2": ""},
        ]

        self.assertEqual(web_app.calculate_averages(rows), {
            "temperature": 15.0,
            "humidity": 50.0,
            "pressure": 1005.0,
            "co2": 500.0,
        })

    def test_averages_report_no_data_as_null(self):
        self.assertEqual(web_app.calculate_averages([]), {
            "temperature": None,
            "humidity": None,
            "pressure": None,
            "co2": None,
        })

    def test_manual_empty_rows(self):
        response = self.client.post(
            "/api/sensor-data/manual",
            json={"rows": []},
        )

        self.assertEqual(response.status_code, 400)

    def test_manual_non_json_body(self):
        response = self.client.post(
            "/api/sensor-data/manual",
            data="not json at all",
            content_type="text/plain",
        )

        self.assertEqual(response.status_code, 400)

    def test_dashboard_contains_manual_view_button(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'data-view-button="manual"', response.data)
        self.assertIn(b"data-manual-submit", response.data)
        self.assertIn(b'data-manual-input="humidity" required', response.data)
        self.assertIn(b'data-manual-input="pressure" required', response.data)
        self.assertIn(b'data-manual-input="co2" required', response.data)
        self.assertIn(b"data-csv-download", response.data)


if __name__ == "__main__":
    unittest.main()
