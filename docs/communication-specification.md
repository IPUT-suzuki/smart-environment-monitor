# 通信仕様

TCPは`SERVER_ADDR:SERVER_PORT`（既定9000）へ接続し、UTF-8 JSONを改行で区切るJSON Lines形式です。1接続で複数行を送れます。

```json
{"client_id":"node-01","region":"tokyo","datetime":"2026-07-29 10:00:00","session_id":"uuid","sequence":1,"sensor_data":{"temperature":25.0,"humidity":50.0,"pressure":1000.0,"co2":500}}
```

必須項目は`client_id`、`region`、`datetime`、`session_id`（空でない文字列）、`sequence`（正整数）、4つ全ての`sensor_data`です。温度・湿度・気圧は有限数かつ小数第1位まで、CO₂は有限な整数です。未知の測定フィールドは拒否します。この測定値ルールはWeb手動登録にも共通で適用します。重複は`client_id`、`session_id`、`sequence`の組合せで判定します。

```json
{"ok":true,"session_id":"uuid","sequence":1,"received_count":4,"duplicate":false}
```

異常時は`{"ok":false,"error":"..."}`を返します。クライアントは`session_id`と`sequence`が一致するACKだけを受理します。ヘルスは`POST /api/health`、更新通知は`GET /api/health/stream`のSSEです。詳細なHTTPパラメータは[Web API](../web/README.md)を参照してください。
