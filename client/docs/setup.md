# clientセットアップ

Raspberry Pi OSでI²CとUARTを有効化し、DHT22を`DHT22_GPIO`へ、BME280をI²Cへ、MH-Z19Cを`SERIAL_PORT`へ接続します。接続先TCPサーバー、端末ID・地域を`client/.env`で設定します。

```bash
cd smart-environment-monitor
source .venv/bin/activate
pip install -r client/requirements.txt
cp client/.env.example client/.env
python -m client.main --mode main --debug
```

実機がない開発では`--mode mock --iterations 10 --no-notify`を使用します。Webhookは`.env`だけに置き、ログやソースへ書きません。
