# データフロー

## 正常系

```mermaid
sequenceDiagram
  participant C as client
  participant S as server
  participant D as sensor_data.csv
  participant W as web
  C->>C: 3センサを読取・有限値を検証
  C->>S: JSON Lines / TCP
  S->>S: スキーマ検証・重複判定
  S->>D: 共通ロック取得後に追記
  S-->>C: ACK(session_id, sequence, received_count)
  C->>W: HTTP health POST
  W->>D: 表示・検索・CSV出力時に共有ロックで読取
```

## 異常系

いずれかのセンサが欠損・非数値・NaN・Infinityなら測定JSONを作らず、該当センサだけを失敗として記録します。TCPエラーやACK不一致では送信失敗を記録します。連続失敗がしきい値に達したときだけDiscord通知し、復旧時は一度だけ通知します。CSVロックがタイムアウトしたWeb APIは503、TCPサーバーは再送可能なエラーACKを返します。
