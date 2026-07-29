# server — データ受信サーバー

TCP 9000番でJSON Linesの測定データを受け、内容を検証して`data/sensor_data.csv`へ保存します。同一`client_id`・`session_id`・`sequence`は重複保存せずACKを返します。各接続は別スレッドで処理し、CSVはWebプロセスと共通のクロスプラットフォームロックで保護します。

## 設定

`server/.env.example`を`server/.env`にコピーします。

| 設定 | 必須 | 既定 | 説明 |
| --- | --- | --- | --- |
| SERVER_ADDR / SERVER_PORT | いいえ | `0.0.0.0` / `9000` | TCP待受 |
| SENSOR_DATA_PATH | いいえ | `data/sensor_data.csv` | リポジトリルート基準の保存先 |
| TCP_MAX_REQUEST_BYTES | いいえ | `1048576` | 1接続の最大受信量 |
| CSV_LOCK_TIMEOUT_SECONDS | いいえ | `5` | ロック待機の上限 |
| CSV_LOCK_STALE_AFTER_SECONDS | いいえ | `60` | 異常終了ロックの回復時間 |

## セットアップ・起動

Linux:

```bash
cd smart-environment-monitor
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r server/requirements.txt
cp server/.env.example server/.env
python -m server.main
```

Windows PowerShell:

```powershell
cd smart-environment-monitor
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r server/requirements.txt
Copy-Item server/.env.example server/.env
python -m server.main
```

`Ctrl+C`で停止します。`--debug`は受信・ACKの診断ログを出します。

## テスト

```bash
python -m unittest discover -s server/tests -v
python -m server.main --mode test --target roundtrip --count 10
```

後者は一時CSV・ローカルTCP・`client`のmockモードを使う結合テストです。本番CSVを書き換えません。

[仕様](./docs/specification.md)、[セットアップ](./docs/setup.md)、[TCP仕様](../docs/communication-specification.md)も参照してください。
