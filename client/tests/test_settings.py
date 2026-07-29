import os
import importlib
import unittest
from unittest.mock import patch

from client.config import settings
from client.config.settings import env_float, env_int


class SettingsTest(unittest.TestCase):
    def test_env_int_uses_default_and_parses_hexadecimal(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("TEST_CLIENT_SETTING", None)
            self.assertEqual(env_int("TEST_CLIENT_SETTING", 26), 26)
        with patch.dict(os.environ, {"TEST_CLIENT_SETTING": "0x76"}, clear=False):
            self.assertEqual(env_int("TEST_CLIENT_SETTING", 0, base=0), 0x76)

    def test_env_int_rejects_values_below_minimum(self):
        with patch.dict(os.environ, {"TEST_CLIENT_SETTING": "0"}, clear=False):
            with self.assertRaisesRegex(ValueError, "at least 1"):
                env_int("TEST_CLIENT_SETTING", 3, minimum=1)

    def test_env_float_rejects_non_positive_values(self):
        with patch.dict(os.environ, {"TEST_CLIENT_SETTING": "0"}, clear=False):
            with self.assertRaisesRegex(ValueError, "greater than 0"):
                env_float("TEST_CLIENT_SETTING", 5)

    def test_env_float_rejects_non_finite_values(self):
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value), patch.dict(os.environ, {"TEST_CLIENT_SETTING": value}, clear=False):
                with self.assertRaisesRegex(ValueError, "greater than 0"):
                    env_float("TEST_CLIENT_SETTING", 5)

    def test_default_send_interval_is_ten_seconds(self):
        with patch.dict(os.environ, {"SEND_INTERVAL_SECONDS": ""}, clear=False):
            importlib.reload(settings)
            self.assertEqual(settings.DEFAULT_SEND_INTERVAL, 10)
        importlib.reload(settings)
        with patch.dict(os.environ, {"TEST_CLIENT_SETTING": "invalid"}, clear=False):
            with self.assertRaisesRegex(ValueError, "must be a number"):
                env_float("TEST_CLIENT_SETTING", 5)


if __name__ == "__main__":
    unittest.main()
