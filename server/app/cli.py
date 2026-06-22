import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", default="main", choices=("main", "test"), help="動作モードの指定")
    parser.add_argument("--server-addr", help="待ち受けサーバーアドレスの指定")
    parser.add_argument("--server-port", type=int, help="待ち受けサーバーポートの指定")
    parser.add_argument("-t","--target", choices=("roundtrip",), help="結合テスト対象")
    parser.add_argument("-c","--count", type=int, default=10, help="結合テストの送信件数")
    parser.add_argument("-d", "--debug", action="store_true", help="デバッグモードで実行")
    return parser.parse_args()
