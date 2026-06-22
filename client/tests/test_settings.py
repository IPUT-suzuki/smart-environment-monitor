import os
import unittest
from unittest.mock import patch

from config.settings import env_float, env_int


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
        with patch.dict(os.environ, {"TEST_CLIENT_SETTING": "invalid"}, clear=False):
            with self.assertRaisesRegex(ValueError, "must be a number"):
                env_float("TEST_CLIENT_SETTING", 5)


if __name__ == "__main__":
    unittest.main()
