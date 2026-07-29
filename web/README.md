# web — Flaskダッシュボード

測定CSVを表・検索・ソート・ページング・グラフで表示し、抽出結果全体の温度、湿度、気圧、CO₂平均を示します。センサー送信形式と同じ4測定値・桁数による手動入力、測定CSV/ヘルス履歴CSV出力、PNGグラフ保存、ヘルス状態とSSEを提供します。

## 設定

`web/.env.example`を`web/.env`にコピーします。

| 設定 | 必須 | 既定 | 説明 |
| --- | --- | --- | --- |
| WEB_HOST / WEB_PORT | いいえ | `0.0.0.0` / `5000` | Flask待受 |
| WEB_DEBUG | いいえ | `false` | 開発用デバッグ |
| SENSOR_DATA_PATH | いいえ | `data/sensor_data.csv` | serverと同じ測定CSV |
| HEALTH_HISTORY_PATH | いいえ | `data/health_history.csv` | ヘルス履歴CSV |
| HEALTH_OFFLINE_AFTER_SECONDS | いいえ | `30` | オフライン判定 |
| CSV_LOCK_TIMEOUT_SECONDS | いいえ | `5` | 共有CSVのロック待機 |

## セットアップ・起動

Linux:

```bash
cd smart-environment-monitor
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r web/requirements.txt
cp web/.env.example web/.env
python -m web.app
```

Windows PowerShell:

```powershell
cd smart-environment-monitor
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r web/requirements.txt
Copy-Item web/.env.example web/.env
python -m web.app
```

`http://localhost:5000/`でダッシュボード、`/api/docs`でAPIドキュメントを開きます。APIドキュメントのPOST試行は初期状態では保存しない検証モードです。実登録を明示的に有効化した場合だけ保存します。`Ctrl+C`で停止します。

## APIとテスト

主なAPIは`GET /api/sensor-data`、`GET /api/sensor-data/search`、`GET /api/sensor-data/download`、`POST /api/sensor-data/manual`、`GET/POST /api/health`、`GET /api/health/<client_id>/download`、`GET /api/health/stream`です。必須/任意パラメータ、入出力スキーマ、curl例は実行中の[/api/docs](/api/docs)および[Web API仕様](./docs/api.md)にあります。

```bash
python -m unittest discover -s web/tests -v
```

自動テストは一時CSVを使います。画面のスマートフォン操作は実機ブラウザで別途確認してください。
