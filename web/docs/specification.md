# web仕様

## API

| メソッド | エンドポイント | 内容 |
| --- | --- | --- |
| GET | `/api/sensor-data` | 全測定値と平均 |
| GET | `/api/sensor-data/search` | 条件・ソート付き測定検索と平均 |
| GET | `/api/sensor-data/download` | 条件・ソート付きUTF-8 BOM CSV |
| POST | `/api/sensor-data/manual` | 4測定値必須、センサーと同じ型・桁数の手動追加 |
| GET / POST | `/api/health` | 最新ヘルス取得 / ヘルス受信 |
| GET | `/api/health/<client_id>/download` | 端末別ヘルスCSV |
| GET | `/api/health/stream` | ヘルス更新SSE |

検索は端末ID、地域、ISO日時、各数値の完全一致・最小・最大に対応します。`sort_by`は保存CSV列名、`sort_order`は`asc`または`desc`です。CSVロックタイムアウトは503、入力不正は400です。

手動入力の本文例:

```json
{"rows":[{"temperature":25.0,"humidity":50.0,"pressure":1000.0,"co2":700}]}
```

全行で温度・湿度・気圧・CO₂が必須です。温度・湿度・気圧は有限数かつ小数第1位まで、CO₂は有限な整数とし、センサー送信データと一致させます。欠損、未知のフィールド、`NaN`、Infinity、真偽値は拒否します。詳細なcurl例は実行中の`/api/docs`にあります。
