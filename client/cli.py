import argparse

from modes.registry import MODE_HANDLERS


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-m",
        "--mode",
        default="main",
        choices=MODE_HANDLERS.keys(),
        help="動作モードの指定",
    )

    parser.add_argument("-t", "--target", help="テスト対象の指定")

    parser.add_argument("--server-addr", help="送信先サーバーアドレスの指定")

    parser.add_argument("--server-port", type=int, help="送信先サーバーポートの指定")

    parser.add_argument(
        "-d", "--debug", action="store_true", help="デバッグモードで実行"
    )

    return parser.parse_args()
