# 要求仕様

## 顧客要求

Raspberry Piをセンサノードにし、DHT22、BME280、MH-Z19Cから温度・湿度・気圧・CO₂を取得します。既定10秒周期で完全な測定スナップショットだけをTCP送信し、受信サーバーが検証・重複排除・CSV保存してACKを返します。PCとスマートフォンのブラウザで表、検索、平均、グラフ、CSVを利用でき、Web手動登録もセンサー送信形式と同じ4測定値・桁数で登録できなければなりません。

## 追加機能

端末ヘルス、オンライン判定、SSE、端末別ヘルス履歴CSV、PNGグラフ保存、Discordの起動・異常・復旧通知を提供します。

| ID | 要求 | 実装の参照 |
| --- | --- | --- |
| R-01 | 既定10秒の取得・送信周期 | `client/config/settings.py` |
| R-02 | TCP JSON Lines、検証、ACK、重複排除 | `client/adapters/outbound/tcp.py`、`server/` |
| R-03 | 測定CSVの安全な共有 | `common/csv_lock.py`、`server/repositories/`、`web/app.py` |
| R-04 | 検索・表示・平均・グラフ | `web/app.py`、`web/static/app.js` |
| R-05 | センサーと同じ4測定値・桁数による手動入力 | `common/measurement_schema.py`、`web/app.py` の `/api/sensor-data/manual` |
| R-06 | 測定CSV・ヘルスCSVの出力 | `web/app.py` の download endpoints |
| R-07 | 自動・結合・実機試験の分離 | `docs/testing.md` |

実装状況の詳細と未確認事項は[実装監査結果](./implementation-audit.md)に記録します。
