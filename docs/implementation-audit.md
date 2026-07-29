# 実装監査結果

監査日は2026-07-29です。作業開始時点では、既定周期4秒、Windows非対応の`fcntl`、プロセス間ロック不足、測定CSVダウンロード未実装、手動入力仕様の不一致、依存関係の混在、テストのimport失敗を確認しました。安全に修正できる項目を実装・自動試験しました。

## 要求仕様マトリクス

| ID | 要件 | 状態 | 根拠 | 対応 |
| --- | --- | --- | --- | --- |
| R-01 | Raspberry Piセンサノード | 実機が必要なため未確認 | `client/app/modes.py` | 実機確認を分離 |
| R-02 | DHT22温湿度 | 実機が必要なため未確認 | `client/adapters/sensors/dht22.py` | 自動試験は失敗処理のみ |
| R-03/R-04 | 既定10秒・設定変更 | 実装済み | `settings.DEFAULT_SEND_INTERVAL`、`test_settings` | 4秒から10秒へ修正 |
| R-05/R-06 | JSON/TCP送信 | 実装済み | `payload.py`、`outbound/tcp.py` | 結合試験済み |
| R-07/R-08 | 検証とACK | 実装済み | `protocol.validate_payload`、`tcp_server.py` | 有限値検証を追加 |
| R-09/R-10 | 重複排除・CSV | 実装済み | `CsvSensorRepository`、`test_csv_repository` | プロセス安全化 |
| R-11 | 不完全値を送らない | 実装済み | `is_valid_sensor_reading`、`test_runtime` | NaNも拒否 |
| R-12/R-13 | 複数端末・識別 | 実装済み | `test_tcp_server` | 同時ACK試験を追加 |
| R-14 | 表示 | 実装済み | `web/templates/index.html` | 自動API試験済み |
| R-15/R-16 | 抽出結果の平均 | 実装済み | `calculate_averages`、`renderAverages` | 空欄・0件を安全化 |
| R-17/R-18/R-19 | 手動追加 | 実装済み | `common/measurement_schema.py`、`/api/sensor-data/manual`、`test_sensor_api` | センサーと同じ4項目・桁数へ統一 |
| R-20 | 表示要求のログ | 実装済み | `web.app.logger.info` | APIごとに記録 |
| R-21 | 単体・結合試験 | 実装済み | `client/server/web/tests`、`roundtrip.py` | テストを拡充 |

## 追加機能

BME280/MH-Z19Cアダプタ、ヘルス状態、SSE、検索・ソート・ページング、グラフ/平均/PNG、ヘルスCSV、Discord通知は実装を確認しました。BME280/MH-Z19Cの実測、Discord実送信、スマートフォン実機は未確認です。mainモードでMH-Z19Cの代わりにダミーを使っていた不具合は修正しました。

## 実施した修正

- `common/csv_lock.py`を追加し、`server`と`web`の読取・書込・移行を共有ロックに統一
- TCP保存時のロックタイムアウトACK、有限値検証、複数クライアント試験を追加
- 測定CSVダウンロード、UTF-8 BOM、0件ヘッダー、検索・ソート反映を追加
- TCP受信とWeb手動入力を4測定値必須・同一桁数の共通検証へ統一し、画面平均カードを追加
- `fcntl`を除去してWindowsでのWeb importを可能にした
- `client`既定周期を10秒へ修正し、mainモードのMH-Z19C実機アダプタを使用
- requirementsをサービス別に分離し、実在LANアドレスをサンプルから除去

## 構成・削除・セキュリティ

新規: `common/`、サービス別README/requirements/docs、共通docs、追加テスト。削除: 旧ルート`requirements.txt`、`requirements-w.txt`（参照を`rg`とREADMEで確認）。移動はありません。`.env`、実測CSV、ロック・移行生成物をGit除外しました。履歴に秘密値が存在した場合は別途履歴書換えが必要ですが、本作業では実行しません。

## テスト結果

| コマンド | 結果 |
| --- | --- |
| `python -m unittest discover -s client/tests -v` | 10件成功 |
| `python -m unittest discover -s server/tests -v` | 9件成功 |
| `python -m unittest discover -s web/tests -v` | 35件成功 |
| `python -m unittest discover -s tests -v` | 4件成功（リンク・エントリーポイント・requirements） |
| `python -m server.main --mode test --target roundtrip --count 10` | 10件送受信、ACK・重複排除成功 |

Windowsの新規仮想環境で、各サービスの個別`requirements.txt`を導入し、`client.app.runtime`、`server.app.main`、`web.app`のimportも確認しました。ローカルWebサーバーはHTTP 200で起動を確認しました。利用可能なブラウザ接続がなかったため、画面の実機レンダリング・スマートフォン操作は未確認です。

## 実機で残る確認

Raspberry Piの各センサ読取・配線、Discord Webhook実送信、実ネットワーク障害、iOS/Android実機操作のみです。
