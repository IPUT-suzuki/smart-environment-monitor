# webセットアップ

Webは`SENSOR_DATA_PATH`で`server`と同じ測定CSVを参照します。両サービスの`CSV_LOCK_TIMEOUT_SECONDS`と`CSV_LOCK_STALE_AFTER_SECONDS`は同じ値にしてください。

```bash
cd smart-environment-monitor
source .venv/bin/activate
pip install -r web/requirements.txt
cp web/.env.example web/.env
python -m web.app
```

Windowsでは仮想環境の有効化に`.venv\Scripts\Activate.ps1`、コピーに`Copy-Item`を使います。ブラウザで`http://localhost:5000/`へアクセスします。
