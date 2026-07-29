# Smart Environment Monitor Web API 仕様

この文書は、`web/app.py` が現在提供しているWeb APIの入出力仕様です。実行中のサーバーでは、同じ内容を操作できるリファレンス画面 `GET /api/docs` でも確認できます。

## 基本情報

| 項目 | 仕様 |
| --- | --- |
| Base URL | `http://<Webサーバーのホスト>:<ポート>` |
| 既定のローカルURL | `http://localhost:5000` |
| JSON文字コード | UTF-8 |
| CSV文字コード | UTF-8 BOM付き |
| 認証 | なし |
| TLS | なし |

認証とTLSは実装されていません。信頼できるLAN内で使用し、インターネットへ直接公開しないでください。外部公開が必要な場合は、リバースプロキシなどでTLS終端と認証を追加してください。

## エンドポイント一覧

| メソッド | パス | 用途 | 成功時 |
| --- | --- | --- | --- |
| GET | `/api/sensor-data` | 測定データの全件取得 | JSON / 200 |
| GET | `/api/sensor-data/search` | 測定データの検索・並べ替え | JSON / 200 |
| GET | `/api/sensor-data/download` | 測定データのCSV保存 | CSV / 200 |
| POST | `/api/sensor-data/manual` | 測定データの手動追加 | JSON / 201 |
| GET | `/api/health` | 端末ごとの最新ヘルス取得 | JSON / 200 |
| POST | `/api/health` | 端末ヘルスの受信 | JSON / 201 |
| GET | `/api/health/<client_id>/download` | 端末別ヘルス履歴のCSV保存 | CSV / 200 |
| GET | `/api/health/stream` | ヘルス更新のSSE購読 | SSE / 200 |

## 共通エラー

JSON APIのエラーは次の形式です。

```json
{
  "error": "エラー内容"
}
```

| ステータス | 条件 |
| --- | --- |
| 400 Bad Request | JSON、クエリ、日時、数値、ソート条件などが不正 |
| 404 Not Found | 指定した端末のヘルス履歴が存在しない |
| 503 Service Unavailable | 共有CSVのロック取得が設定時間内に完了しない |

CSVロック待機時間は `CSV_LOCK_TIMEOUT_SECONDS` で設定します。

## 測定データの共通スキーマ

CSVと `rows` の1要素は次のフィールドを持ちます。CSVから読み込んだJSON値は文字列です。

| フィールド | 内容 |
| --- | --- |
| `client_id` | 端末ID |
| `region` | 地域 |
| `datetime` | 測定日時 |
| `session_id` | 接続・手動入力セッションID |
| `sequence` | セッション内の送信番号 |
| `temperature` | 温度 |
| `humidity` | 湿度 |
| `pressure` | 気圧 |
| `co2` | CO2濃度 |

---

## GET `/api/sensor-data`

保存済みの測定データを日時の新しい順で全件返します。クエリパラメータはありません。

### レスポンス

| フィールド | 型 | 内容 |
| --- | --- | --- |
| `csv_path` | string | 参照中の測定CSVパス |
| `fieldnames` | string[] | CSVの列名 |
| `field_labels` | object | 列名に対応する日本語ラベル |
| `rows` | object[] | 測定データ。新しい日時が先 |
| `row_count` | integer | 全件数 |
| `averages` | object | 温度、湿度、気圧、CO2の平均 |

平均値は、有効な有限数だけで計算します。対象となる有効値がない項目は `null` です。

```bash
curl "http://localhost:5000/api/sensor-data"
```

```json
{
  "csv_path": "data/sensor_data.csv",
  "fieldnames": [
    "client_id",
    "region",
    "datetime",
    "session_id",
    "sequence",
    "temperature",
    "humidity",
    "pressure",
    "co2"
  ],
  "field_labels": {
    "client_id": "端末ID",
    "region": "地域",
    "datetime": "日時",
    "session_id": "セッションID",
    "sequence": "送信番号",
    "temperature": "温度",
    "humidity": "湿度",
    "pressure": "気圧",
    "co2": "CO2"
  },
  "rows": [],
  "row_count": 0,
  "averages": {
    "temperature": null,
    "humidity": null,
    "pressure": null,
    "co2": null
  }
}
```

成功時は `200 OK`、CSVロックのタイムアウト時は `503 Service Unavailable` です。

---

## GET `/api/sensor-data/search`

測定データへ全検索条件をANDで適用し、指定した順序で返します。パラメータはすべて任意です。

### クエリパラメータ

| 名前 | 型・値 | 既定値 | 内容 |
| --- | --- | --- | --- |
| `client_id` | string | 空 | 端末ID |
| `client_id_match` | `contains` / `equals` | `contains` | 端末IDの一致方法 |
| `region` | string | 空 | 地域 |
| `region_match` | `contains` / `equals` | `contains` | 地域の一致方法 |
| `datetime_from` | ISO 8601 | 空 | この日時以上 |
| `datetime_to` | ISO 8601 | 空 | この日時以下 |
| `temperature` | finite number | 空 | 温度の完全一致 |
| `temperature_min` | finite number | 空 | 温度の下限 |
| `temperature_max` | finite number | 空 | 温度の上限 |
| `humidity` / `humidity_min` / `humidity_max` | finite number | 空 | 湿度の一致・下限・上限 |
| `pressure` / `pressure_min` / `pressure_max` | finite number | 空 | 気圧の一致・下限・上限 |
| `co2` / `co2_min` / `co2_max` | finite number | 空 | CO2の一致・下限・上限 |
| `sort_by` | 測定CSVの列名 | `datetime` | 並べ替える列 |
| `sort_order` | `asc` / `desc` | `desc` | 昇順または降順 |

`contains` は大文字・小文字を区別しない部分一致、`equals` は大文字・小文字を区別する完全一致です。日時にタイムゾーンがない場合はJSTとして扱います。開始日時は終了日時以下、各最小値は最大値以下である必要があります。

`sort_by` に指定できる値は `client_id`、`region`、`datetime`、`session_id`、`sequence`、`temperature`、`humidity`、`pressure`、`co2` です。

### レスポンス

`GET /api/sensor-data` のレスポンスに、正規化した検索条件を示す `filters` が加わります。`rows`、`row_count`、`averages` は抽出結果だけを対象にします。

```bash
curl "http://localhost:5000/api/sensor-data/search?client_id=node&temperature_min=20&temperature_max=30&sort_by=temperature&sort_order=asc"
```

成功時は `200 OK`、条件が不正な場合は `400 Bad Request`、CSVロックのタイムアウト時は `503 Service Unavailable` です。

---

## GET `/api/sensor-data/download`

検索APIと同じ条件・並び順を適用した測定データをCSVで返します。

- クエリ仕様は `GET /api/sensor-data/search` と同じです。
- CSVは保存中の測定CSVと同じ列順です。
- 0件でもヘッダー行を返します。
- 文字コードはUTF-8 BOM付き、改行はCRLFです。
- `Content-Type` は `text/csv` です。
- ダウンロード名は `sensor-data-YYYYMMDD-HHMMSS.csv` です。

```bash
curl -OJ "http://localhost:5000/api/sensor-data/download?region=tokyo&sort_order=desc"
```

成功時は `200 OK`、条件が不正な場合は `400 Bad Request`、CSVロックのタイムアウト時は `503 Service Unavailable` です。

---

## POST `/api/sensor-data/manual`

Web入力用の測定値を1行以上まとめて保存します。全行の検証に成功した場合だけCSVへ追記します。

### クエリパラメータ

| 名前 | 型・値 | 既定値 | 内容 |
| --- | --- | --- | --- |
| `dry_run` | boolean | `false` | `true`なら入力検証だけを行い、CSVへ保存しない |

`true`には`1`、`true`、`yes`、`on`、`false`には`0`、`false`、`no`、`off`を指定できます。大文字・小文字は区別しません。それ以外の値は、安全のため登録せず `400 Bad Request` を返します。

### リクエスト

`Content-Type: application/json`

```json
{
  "rows": [
    {
      "temperature": 25.0,
      "humidity": 50.0,
      "pressure": 1000.0,
      "co2": 700
    },
    {
      "temperature": 26.0,
      "humidity": 55.0,
      "pressure": 1001.0,
      "co2": 750
    }
  ]
}
```

| フィールド | 必須 | 仕様 |
| --- | --- | --- |
| `rows` | 必須 | 空ではない配列。各要素は次の4項目だけを持つobject |
| `rows[].temperature` | 必須 | number（°C）、小数第1位まで |
| `rows[].humidity` | 必須 | number（%）、小数第1位まで |
| `rows[].pressure` | 必須 | number（hPa）、小数第1位まで |
| `rows[].co2` | 必須 | integer（ppm） |

4測定値の型と桁数はセンサーノードがTCP送信する `sensor_data` と同じです。`temperature`、`humidity`、`pressure` は整数値も受け付けますが、CSVには小数第1位までの形式（例: `25.0`）で保存します。`co2` は整数だけを受け付けます。未指定、空文字列、boolean、NaN、Infinity、未知のフィールドは拒否します。

保存時に次の値をサーバーが補います。

| フィールド | 保存値 |
| --- | --- |
| `client_id` | `web-manual` |
| `region` | `web-input` |
| `datetime` | 受信時点のJST |
| `session_id` | `web-manual-<UUID>` |
| `sequence` | リクエスト内の1始まりの行番号 |

```bash
curl -X POST "http://localhost:5000/api/sensor-data/manual" \
  -H "Content-Type: application/json" \
  -d '{"rows":[{"temperature":25.0,"humidity":50.0,"pressure":1000.0,"co2":700}]}'
```

### 成功レスポンス

`201 Created`

```json
{
  "rows_added": 1,
  "session_id": "web-manual-<UUID>"
}
```

JSONや測定値が不正な場合は `400 Bad Request`、CSVロックのタイムアウト時は `503 Service Unavailable` です。

### 検証のみのレスポンス

`dry_run=true` の場合は同じ入力検証を行いますが、測定CSVの作成・更新は行いません。成功時は `200 OK` です。

```bash
curl -X POST "http://localhost:5000/api/sensor-data/manual?dry_run=true" \
  -H "Content-Type: application/json" \
  -d '{"rows":[{"temperature":25.0,"humidity":50.0,"pressure":1000.0,"co2":700}]}'
```

```json
{
  "valid": true,
  "dry_run": true,
  "rows_validated": 1
}
```

---

## GET `/api/health`

端末ごとの最新ヘルスを端末IDの昇順で返します。オンライン・オフラインは、最終受信時刻と現在時刻の差が `HEALTH_OFFLINE_AFTER_SECONDS` 以下かどうかで判定します。

### クエリパラメータ

| 名前 | 型 | 内容 |
| --- | --- | --- |
| `client_id` | string | 端末IDの大文字・小文字を区別しない部分一致 |
| `region` | string | 地域の大文字・小文字を区別しない部分一致 |

### レスポンス

```json
{
  "offline_after_seconds": 30,
  "filters": {
    "client_id": "",
    "region": ""
  },
  "clients": [
    {
      "client": {
        "client_id": "node-01",
        "region": "tokyo"
      },
      "sensor": {},
      "server_send": {},
      "health_report": {},
      "runtime": {},
      "received_at": "2026-07-29T10:00:00+09:00",
      "status": "online"
    }
  ]
}
```

`clients` 内の `sensor`、`server_send`、`health_report`、`runtime` はPOSTされた構造を保持します。`received_at` と `status` はWebサーバーが付加します。

```bash
curl "http://localhost:5000/api/health?client_id=node&region=tokyo"
```

成功時は `200 OK` です。

---

## POST `/api/health`

センサノードからヘルス状態を受信します。ヘルス履歴CSVへ追記し、端末の最新状態を更新した後、SSE購読者へ `health` イベントを通知します。

### クエリパラメータ

| 名前 | 型・値 | 既定値 | 内容 |
| --- | --- | --- | --- |
| `dry_run` | boolean | `false` | `true`なら入力検証だけを行い、履歴・最新状態を更新せずSSEも通知しない |

指定可能な真偽値は手動測定データPOSTと同じです。不正な値は登録せず `400 Bad Request` を返します。

### リクエスト全体

`Content-Type: application/json`

トップレベルには `client`、`sensor`、`server_send`、`health_report`、`runtime` の5つのobjectがすべて必要です。

### `client`

| フィールド | 型 | 条件 |
| --- | --- | --- |
| `client_id` | string | 必須、空文字列不可 |
| `region` | string | 必須、空文字列不可 |

### `sensor`

`bme280`、`dht22`、`mhz19c` の3 objectがすべて必要です。各センサーは同じフィールドを持ちます。

| フィールド | 型 | 条件 |
| --- | --- | --- |
| `name` | string | 必須。空文字列は許容 |
| `connect` | boolean | 必須 |
| `read` | boolean | 必須 |
| `read_count` | integer | 必須、0以上、boolean不可 |
| `fail_count` | integer | 必須、0以上、boolean不可 |
| `consecutive_fail_count` | integer | 必須、0以上、boolean不可 |
| `last_success_at` | string | 必須。空文字列は許容 |
| `last_failed_at` | string | 必須。空文字列は許容 |
| `error` | string | 必須。空文字列は許容 |

### `server_send`

| フィールド | 型 | 条件 |
| --- | --- | --- |
| `success` | boolean | 必須 |
| `success_count` | integer | 必須、0以上 |
| `received_count` | integer | 必須、0以上 |
| `last_ack_sequence` | integer | 必須、0以上 |
| `fail_count` | integer | 必須、0以上 |
| `consecutive_fail_count` | integer | 必須、0以上 |
| `last_status_code` | integer | 必須、0以上 |
| `last_success_at` | string | 必須 |
| `last_failed_at` | string | 必須 |
| `error` | string | 必須 |

### `health_report`

| フィールド | 型 | 条件 |
| --- | --- | --- |
| `success` | boolean | 必須 |
| `success_count` | integer | 必須、0以上 |
| `fail_count` | integer | 必須、0以上 |
| `consecutive_fail_count` | integer | 必須、0以上 |
| `last_status_code` | integer | 必須、0以上 |
| `last_success_at` | string | 必須 |
| `last_failed_at` | string | 必須 |
| `error` | string | 必須 |

### `runtime`

| フィールド | 型 | 条件 |
| --- | --- | --- |
| `started_at` | string | 必須、空文字列不可 |
| `last_loop_at` | string | 必須。空文字列は許容 |
| `loop_count` | integer | 必須、0以上 |
| `uptime_seconds` | integer | 必須、0以上 |

時刻を表すフィールドはサーバー側では文字列型だけを検証し、ISO 8601形式そのものは検証しません。

### リクエスト例

```json
{
  "client": {
    "client_id": "node-01",
    "region": "tokyo"
  },
  "sensor": {
    "bme280": {
      "name": "BME280",
      "connect": true,
      "read": true,
      "read_count": 1,
      "fail_count": 0,
      "consecutive_fail_count": 0,
      "last_success_at": "2026-07-29T10:00:00+09:00",
      "last_failed_at": "",
      "error": ""
    },
    "dht22": {
      "name": "DHT22",
      "connect": true,
      "read": true,
      "read_count": 1,
      "fail_count": 0,
      "consecutive_fail_count": 0,
      "last_success_at": "2026-07-29T10:00:00+09:00",
      "last_failed_at": "",
      "error": ""
    },
    "mhz19c": {
      "name": "MHZ19C",
      "connect": true,
      "read": true,
      "read_count": 1,
      "fail_count": 0,
      "consecutive_fail_count": 0,
      "last_success_at": "2026-07-29T10:00:00+09:00",
      "last_failed_at": "",
      "error": ""
    }
  },
  "server_send": {
    "success": true,
    "success_count": 1,
    "received_count": 1,
    "last_ack_sequence": 1,
    "fail_count": 0,
    "consecutive_fail_count": 0,
    "last_success_at": "2026-07-29T10:00:00+09:00",
    "last_failed_at": "",
    "last_status_code": 0,
    "error": ""
  },
  "health_report": {
    "success": true,
    "success_count": 1,
    "fail_count": 0,
    "consecutive_fail_count": 0,
    "last_success_at": "2026-07-29T10:00:00+09:00",
    "last_failed_at": "",
    "last_status_code": 201,
    "error": ""
  },
  "runtime": {
    "started_at": "2026-07-29T09:00:00+09:00",
    "last_loop_at": "2026-07-29T10:00:00+09:00",
    "loop_count": 1,
    "uptime_seconds": 3600
  }
}
```

### 成功レスポンス

`201 Created`

```json
{
  "client_id": "node-01",
  "received_at": "2026-07-29T10:00:01+09:00"
}
```

JSON構造やフィールド型が不正な場合は `400 Bad Request`、CSVロックのタイムアウト時は `503 Service Unavailable` です。

### 検証のみのレスポンス

`dry_run=true` の場合は同じスキーマ検証を行いますが、ヘルス履歴CSV、端末の最新状態、SSE通知を変更しません。成功時は `200 OK` です。

```json
{
  "valid": true,
  "dry_run": true,
  "client_id": "node-01"
}
```

---

## GET `/api/health/<client_id>/download`

URLパスの `client_id` と完全一致する端末の全ヘルス履歴をCSVで返します。

- 文字コードはUTF-8 BOM付き、改行はCRLFです。
- 列順はサーバーのヘルス履歴スキーマと同じです。
- `Content-Type` は `text/csv` です。
- ファイル名は `health-<safe-client-id>.csv` です。
- ファイル名で英数字、ピリオド、アンダースコア、ハイフン以外の文字は `_` へ置換します。

```bash
curl -OJ "http://localhost:5000/api/health/node-01/download"
```

成功時は `200 OK`、該当履歴がない場合は `404 Not Found`、CSVロックのタイムアウト時は `503 Service Unavailable` です。

404レスポンス:

```json
{
  "error": "health history not found"
}
```

---

## GET `/api/health/stream`

端末ヘルス更新をServer-Sent Events（SSE）で購読します。

### レスポンスヘッダー

| ヘッダー | 値 |
| --- | --- |
| `Content-Type` | `text/event-stream` |
| `Cache-Control` | `no-cache` |
| `X-Accel-Buffering` | `no` |

接続直後に再接続間隔を送り、`POST /api/health` の成功ごとに `health` イベントを送ります。更新がない間は設定された間隔でkeepaliveコメントを送ります。

```text
retry: 3000

event: health
data: updated

: keepalive
```

JavaScriptの利用例:

```javascript
const stream = new EventSource("/api/health/stream");

stream.addEventListener("health", (event) => {
  console.log(event.data); // "updated"
});

// 終了時
stream.close();
```

成功時は接続を維持したまま `200 OK` を返します。再接続ミリ秒は `HEALTH_STREAM_RETRY_MILLISECONDS`、keepalive秒数は `HEALTH_STREAM_KEEPALIVE_SECONDS` で設定します。

## ブラウザ上のAPIリファレンス

Webサーバー起動後に `http://localhost:5000/api/docs` を開くと、次の操作をブラウザ上で行えます。

- GET APIの実行とJSONレスポンス表示
- 測定データ検索のクエリ組み立て
- 測定CSVと端末別ヘルスCSVの保存
- 手動測定値と端末ヘルスJSONの編集・保存しない検証
- 実登録を明示的に有効化した場合だけPOSTによる保存
- URL、curl例、レスポンスのコピー
- SSEの接続、切断、イベント確認
