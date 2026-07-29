import unittest

from client.adapters.outbound.discord import notify_discord


class DiscordNotificationTest(unittest.TestCase):
    def test_missing_or_invalid_webhook_is_a_safe_noop(self):
        self.assertFalse(notify_discord(None, "message"))
        self.assertFalse(notify_discord("https://example.invalid/webhook", "message"))
