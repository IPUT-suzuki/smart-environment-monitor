# Smart Environment Monitor システム構成図

```mermaid
flowchart LR
    subgraph Edge["計測端末（Raspberry Pi）"]
        direction TB
        Sensors["DHT22：温度・湿度<br/>BME280：気圧<br/>MH-Z19C：CO2"]
        Runtime["MonitorRuntime<br/>センサー読み取り・状態管理"]
        SensorSender["測定データ送信"]
        HealthReporter["ヘルスログ送信"]
        DiscordNotifier["Discord通知"]

        Sensors -->|"GPIO / I2C / UART"| Runtime
        Runtime --> SensorSender
        Runtime --> HealthReporter
        Runtime --> DiscordNotifier
    end

    subgraph Monorepo["Smart Environment Monitor（モノレポ）"]
        direction TB

        subgraph CollectionServer["データ収集サーバー（server/）"]
            TcpServer["Python TCP Server<br/>受信・検証・重複排除"]
        end

        subgraph SharedStorage["共有データストレージ（data/）"]
            direction TB
            SensorData[("sensor_data.csv<br/>センサー測定履歴")]
            HealthData[("health_history.csv<br/>端末ヘルス履歴")]
        end

        subgraph WebServer["Web サーバー（web/）"]
            direction TB
            SensorApi["Flask：測定データAPI<br/>参照・検索・手動入力"]
            HealthApi["Flask：ヘルスAPI / SSE<br/>受信・履歴保存<br/>LATEST_HEALTHを更新・参照"]
        end

        TcpServer -->|"測定データを保存"| SensorData
        SensorData <-->|"履歴参照・手動入力保存"| SensorApi
        HealthApi <-->|"履歴保存・起動時復元"| HealthData
    end

    subgraph UserAccess["利用者の確認経路"]
        direction TB

        subgraph DashboardAccess["Webブラウザ：ダッシュボード"]
            direction TB
            SensorView["測定値・グラフ・検索<br/>CSV取得・手動入力"]
            HealthView["ヘルス状態表示<br/>SSE更新・履歴CSV取得"]
        end

        subgraph NotificationAccess["外部通知"]
            DiscordChannel["Discord<br/>特定の通知チャンネル"]
        end

        User["利用者"]
        SensorView -->|"画面を表示"| User
        HealthView -->|"画面を表示"| User
        DiscordChannel -->|"通知を表示"| User
    end

    SensorSender <-->|"TCP :9000 / JSON Lines<br/>測定データ・保存完了ACK"| TcpServer
    HealthReporter -->|"HTTP POST /api/health"| HealthApi
    DiscordNotifier -->|"Discord Webhook<br/>障害・復旧・起動停止"| DiscordChannel
    SensorApi <-->|"HTTP / JSON"| SensorView
    HealthApi <-->|"HTTP / JSON / SSE"| HealthView
```

## 1. クライアント構成（client/）

センサー読み取り、状態管理、外部送信を担当するRaspberry Pi側のプロセスです。

```mermaid
flowchart LR
    Hardware["DHT22 / BME280 / MH-Z19C"]

    subgraph Client["センサークライアント（client/）"]
        direction LR

        subgraph Startup["起動・設定"]
            direction TB
            Entry["main.py / CLI"]
            Modes["main / mock / test モード"]
            Config["config/settings.py<br/>環境変数・接続先・しきい値"]

            Entry --> Modes
            Config --> Modes
        end

        subgraph Application["アプリケーション"]
            direction TB
            Runtime["MonitorRuntime<br/>定期実行・状態管理"]
            SensorSuite["SensorSuite<br/>3センサーの読み取り統合"]

            Modes --> Runtime
            Modes --> SensorSuite
            SensorSuite -->|"測定値"| Runtime
        end

        subgraph Domain["ドメイン"]
            direction TB
            Payload["payload.py<br/>測定ペイロード生成"]
            Health["health.py / models.py<br/>ヘルス状態・失敗回数"]

            Runtime --> Payload
            Runtime <-->|"状態更新・参照"| Health
        end

        subgraph Outbound["外部通信アダプター"]
            direction TB
            TcpAdapter["tcp.py<br/>測定データ送信・ACK確認"]
            HealthAdapter["health.py<br/>ヘルスログ送信"]
            DiscordAdapter["discord.py<br/>障害・復旧通知"]

            Payload --> TcpAdapter
            Health --> HealthAdapter
            Health --> DiscordAdapter
        end
    end

    Hardware -->|"GPIO / I2C / UART"| SensorSuite
    TcpAdapter -->|"TCP / JSON Lines"| TcpExternal["データ収集サーバー"]
    HealthAdapter -->|"HTTP POST"| WebExternal["Webサーバー"]
    DiscordAdapter -->|"Webhook"| DiscordExternal["Discord通知チャンネル"]
```

3センサーすべての読み取り成功時のみ、測定データをTCP送信します。

## 2. データ収集サーバー構成（server/）

TCPで測定データを受信し、検証・重複排除後に共有CSVへ保存します。

```mermaid
flowchart LR
    ClientExternal["センサークライアント"]

    subgraph Server["データ収集サーバー（server/）"]
        direction LR

        subgraph Startup["起動・設定"]
            Entry["main.py / CLI"]
            Mode["mainモード"]
            Config["config/settings.py<br/>待受先・タイムアウト・保存先"]

            Entry --> Mode
            Config --> Mode
        end

        subgraph Adapter["受信アダプター"]
            TcpServer["SensorTcpServer<br/>接続受付・JSON Lines受信<br/>接続ごとのスレッド処理"]
        end

        subgraph Domain["検証"]
            Validator["domain/protocol.py<br/>ペイロード形式・型検証"]
        end

        subgraph Repository["保存"]
            CsvRepository["CsvSensorRepository<br/>重複排除・CSV変換<br/>受信件数管理"]
        end

        Mode --> TcpServer
        TcpServer --> Validator
        Validator -->|"検証成功"| CsvRepository
    end

    ClientExternal <-->|"TCP :9000<br/>測定データ・保存完了ACK"| TcpServer
    CsvRepository -->|"追記"| SensorData[("共有 sensor_data.csv")]
```

重複判定には `client_id`・`session_id`・`sequence` の組み合わせを使用します。

## 3. Webダッシュボード構成（web/）

測定データの表示・検索・手動入力と、ヘルスログの受信・表示を担当します。

```mermaid
flowchart LR
    Browser["利用者のWebブラウザ"]
    ClientExternal["センサークライアント"]

    subgraph Web["Webダッシュボード（web/）"]
        direction LR

        subgraph Startup["起動・設定"]
            direction TB
            Entry["app.py / Flask<br/>HTTPリクエスト受付"]
            Config["config/settings.py<br/>待受先・CSVパス・SSE設定"]

            Config --> Entry
        end

        subgraph Routes["Flaskルート"]
            direction TB
            Pages["画面ルート<br/>/ ・ /api/docs"]
            SensorApi["測定データAPI<br/>一覧・検索・手動入力"]
            HealthApi["ヘルスAPI<br/>受信・一覧・CSV取得・SSE"]

            Entry --> Pages
            Entry --> SensorApi
            Entry --> HealthApi
        end

        subgraph Presentation["画面"]
            direction TB
            Templates["Jinja2テンプレート<br/>index.html / api_docs.html"]
            Frontend["JavaScript / CSS<br/>一覧・グラフ・検索・モーダル"]

            Pages --> Templates
            Templates --> Frontend
        end

        subgraph HealthState["ヘルス表示状態"]
            direction TB
            LatestHealth["LATEST_HEALTH<br/>Webプロセス内キャッシュ"]
            SseSubscribers["SSE購読管理<br/>更新イベント・keepalive"]

            HealthApi <-->|"最新状態を更新・参照"| LatestHealth
            HealthApi -->|"更新を通知"| SseSubscribers
        end
    end

    Browser <-->|"HTTP<br/>HTML / JSON / SSE"| Entry
    ClientExternal -->|"HTTP POST<br/>ヘルスログ"| Entry

    SensorApi <-->|"参照・手動入力"| SensorData[("共有 sensor_data.csv")]
    HealthApi <-->|"履歴保存・起動時読込"| HealthData[("共有 health_history.csv")]
```

Webサーバーとデータ収集サーバーは、同じ `sensor_data.csv` を参照します。`LATEST_HEALTH` は表示用キャッシュで、ヘルス履歴は `health_history.csv` に保存します。

## 運用上の前提

- `client/`・`server/`・`web/` は、それぞれ独立したプロセスとして起動します。
- `server/` と `web/` の `SENSOR_DATA_PATH` は、同じCSVを指定します。
- TCP受信とWeb APIは、信頼できるLAN内での利用を前提とします。
