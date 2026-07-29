# serverセットアップ

`SERVER_ADDR`と`SERVER_PORT`はTCP待受、`SENSOR_DATA_PATH`はリポジトリルートからのCSV保存先です。Webと同じ測定CSVを設定してください。

```powershell
cd smart-environment-monitor
.venv\Scripts\Activate.ps1
pip install -r server/requirements.txt
Copy-Item server/.env.example server/.env
python -m server.main --debug
```

LinuxではPowerShellの有効化・コピーコマンドを`source .venv/bin/activate`と`cp`に置き換えます。
