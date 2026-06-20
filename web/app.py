import csv
from pathlib import Path

from flask import Flask, jsonify, render_template

BASE_DIR = Path(__file__).resolve().parents[1]
CSV_CANDIDATES = [
    BASE_DIR / "data" / "sensor_data.csv",
]
FIELD_LABELS = {
    "client_id": "端末ID",
    "region": "地域",
    "datetime": "日時",
    "temperature": "温度",
    "humidity": "湿度",
    "pressure": "気圧",
    "co2": "CO2",
}

app = Flask(__name__)


def find_csv_path():
    for path in CSV_CANDIDATES:
        if path.exists():
            return path
    return CSV_CANDIDATES[0]


def load_sensor_rows():
    csv_path = find_csv_path()

    if not csv_path.exists():
        return csv_path, [], []

    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    rows.reverse()
    return csv_path, fieldnames, rows


def sensor_payload():
    csv_path, fieldnames, rows = load_sensor_rows()
    return {
        "csv_path": str(csv_path.relative_to(BASE_DIR)),
        "fieldnames": fieldnames,
        "field_labels": FIELD_LABELS,
        "rows": rows,
        "row_count": len(rows),
    }


@app.route("/")
def index():
    return render_template("index.html", **sensor_payload())


@app.route("/api/sensor-data")
def sensor_data():
    return jsonify(sensor_payload())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
