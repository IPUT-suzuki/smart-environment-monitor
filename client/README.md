# client — センサノード

Raspberry PiでDHT22、BME280、MH-Z19Cを読み、完全な測定セットをTCP受信サーバーへ送信します。読取失敗・NaN・Infinity・欠損時は部分送信せず、次周期で再試行します。ヘルスはWebへHTTP送信し、Discord通知は連続失敗のしきい値と復旧を制御します。

## 前提条件

Python 3.10以上、Raspberry Pi OS/Linux、DHT22、BME280（I²C）、MH-Z19C（UART）が必要です。Windowsでは`mock`モードと自動テストのみを利用してください。TCPは既定9000番を使います。

## 設定

`client/.env.example`を`client/.env`にコピーして、実環境の値へ変更します。

| 設定 | 必須 | 既定 | 説明 |
| --- | --- | --- | --- |
| SERVER_ADDR / SERVER_PORT | はい | `127.0.0.1` / `9000` | TCP受信先 |
| CLIENT_ID / CLIENT_REGION | はい | `client-unknown` / `unknown` | 送信元識別子 |
| SEND_INTERVAL_SECONDS | いいえ | `10` | 測定・送信周期 |
| HEARTBEAT_INTERVAL_SECONDS | いいえ | `10` | ヘルス送信周期 |
| WEB_HEALTH_URL | いいえ | 空 | ヘルスPOST先 |
| DISCORD_WEBHOOK_URL | いいえ | 空 | 秘密値。コミット禁止 |
| DHT22_GPIO / BME280_ADDR | いいえ | `26` / `0x76` | 配線設定 |
| SERIAL_PORT / SERIAL_BAUDRATE | いいえ | `/dev/serial0` / `9600` | MH-Z19C UART |

## セットアップと起動

Linux / Raspberry Pi:

```bash
cd smart-environment-monitor
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r client/requirements.txt
cp client/.env.example client/.env
python -m client.main --mode main
```

Windows PowerShell（ダミーセンサ）:

```powershell
cd smart-environment-monitor
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r client/requirements.txt
Copy-Item client/.env.example client/.env
python -m client.main --mode mock --iterations 10 --no-notify
```

`Ctrl+C`で終了します。`--debug`で詳細ログ、`--server-addr`と`--server-port`で一時的な送信先上書きができます。

## テスト

```bash
python -m unittest discover -s client/tests -v
python -m client.main --mode test --target dht22
python -m client.main --mode test --target bme280
python -m client.main --mode test --target mhz19c
```

後半の3コマンドは実機専用です。Discord実送信試験もWebhookを設定した隔離環境でのみ実行してください。

詳しくは[仕様](./docs/specification.md)、[セットアップ](./docs/setup.md)、[通信仕様](../docs/communication-specification.md)を参照してください。
