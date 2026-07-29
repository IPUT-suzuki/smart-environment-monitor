# テスト仕様

## 自動テスト

すべてリポジトリルートで実行し、本番の`data/`を使用しません。

```bash
python -m unittest discover -s client/tests -v
python -m unittest discover -s server/tests -v
python -m unittest discover -s web/tests -v
python -m server.main --mode test --target roundtrip --count 10
```

| 範囲 | 主な確認 |
| --- | --- |
| client | 既定10秒、環境値、NaN拒否、部分送信抑止、通知のしきい値 |
| server | JSON検証、重複排除、複数TCP接続、ACK、別プロセスのCSV書込み |
| web | 検索、平均、温度だけの手動追加、NaN/Infinity拒否、CSV BOM/0件、ヘルスAPI/SSE |
| roundtrip | client mock → TCP receiver → 一時CSV → ACK/重複排除 |

## 実機確認

以下は自動試験済みとは見なしません。

- Raspberry PiでDHT22、BME280、MH-Z19Cが各配線・設定で読めること
- 実機の起動・Ctrl+C・異常終了時のDiscord通知
- 実ネットワークの再接続・タイムアウト
- iOS/Android実機の表横スクロール、手動入力、CSV/PNGダウンロード

Windowsでは`python -m web.app`の起動とWebテスト、Linuxでは同じコマンドとRaspberry Pi実機試験を確認します。
