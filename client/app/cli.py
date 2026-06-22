import argparse

from tests.targets import TEST_TARGETS


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", default="main", choices=("main", "mock", "test"), help="動作モードの指定")
    targets = ", ".join((*TEST_TARGETS, "all"))
    parser.add_argument("-t", "--target", help=f"テスト対象の指定 ({targets})")
    parser.add_argument("--server-addr", help="送信先サーバーアドレスの指定")
    parser.add_argument("--server-port", type=int, help="送信先サーバーポートの指定")
    parser.add_argument("--iterations", type=int, help="指定回数のループ後に終了（テスト用）")
    parser.add_argument("--interval", type=float, help="送信間隔秒数の上書き（テスト用）")
    parser.add_argument("--no-notify", action="store_true", help="Discord 通知を無効化（結合テスト用）")
    parser.add_argument("-d", "--debug", action="store_true", help="デバッグモードで実行")
    return parser.parse_args()
