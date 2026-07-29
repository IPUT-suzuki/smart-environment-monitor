# リポジトリ構成

```text
.
├── client/                 # Raspberry Pi センサノード
│   ├── adapters/ app/ config/ domain/ tests/
│   ├── docs/
│   ├── .env.example
│   └── requirements.txt
├── server/                 # TCP測定受信サーバー
│   ├── adapters/ app/ config/ domain/ repositories/ tests/
│   ├── docs/
│   ├── .env.example
│   └── requirements.txt
├── web/                    # Flask UI/API
│   ├── config/ static/ templates/ tests/ docs/
│   ├── .env.example
│   └── requirements.txt
├── common/                 # 共有測定値検証・CSVスキーマ・排他ロック
├── data/.gitkeep           # 実行時CSVの配置先
├── docs/                   # リポジトリ共通仕様・監査
└── requirements-dev.txt    # 全サービス開発用の集約参照
```

各サービスは自身の`requirements.txt`と`.env.example`だけを持ちます。Raspberry Pi固有依存を`client`だけへ、Flaskを`web`だけへ配置しました。CSV実データ、`.env`、`*.csv.lock/`、一時移行ファイルは`.gitignore`対象です。

旧ルートの`requirements.txt`と`requirements-w.txt`は依存が混在・重複しており、コードや文書から参照されないことを確認して削除しました。代わりにサービス別requirementsと、任意の開発用`requirements-dev.txt`を置いています。`docs/system-architecture.md`は作業開始時点で利用者の削除状態だったため、復元・変更していません。
