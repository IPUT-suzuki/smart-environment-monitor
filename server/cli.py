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

    parser.add_argument("--server-addr", help="待ち受けサーバーアドレスの指定")

    parser.add_argument("--server-port", type=int, help="待ち受けサーバーポートの指定")

    parser.add_argument(
        "-d", "--debug", action="store_true", help="デバッグモードで実行"
    )

    return parser.parse_args()
