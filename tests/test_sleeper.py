import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from agents.sleeper import Sleeper
from globals.errors import CustomTimeoutError

PATH_TO_SIMULATION_RESULT = Path(Path(__file__).parent, "samples", "simulation_result.csv")
MOCK_STRINGS = {
    "open": "builtins.open",
    "sleep": "time.sleep",
}


class TestSleeper(unittest.TestCase):

    def test_sleep_until_success(self):
        mock_function = MagicMock(side_effect=[False, False, True])

        with patch(MOCK_STRINGS["sleep"]) as mock_sleep:
            Sleeper.until_true(mock_function)
            mock_sleep.assert_called_with(0.01)

        self.assertEqual(mock_function.call_count, 3)

    def test_sleep_until_timeout(self):
        mock_function = MagicMock(return_value=False)

        with patch(MOCK_STRINGS["sleep"]) as mock_sleep:
            with self.assertRaises(CustomTimeoutError):
                Sleeper.until_true(mock_function, timeout=0.02)
                mock_sleep.assert_called_with(0.01)

    def test_sleep_until_file_is_available_IOError(self):
        with (
                patch(MOCK_STRINGS["open"], mock_open(read_data="")) as mock_open_file,
                patch(MOCK_STRINGS["sleep"]) as mock_sleep,
                self.assertRaises(CustomTimeoutError)):
            mock_open_file.side_effect = IOError
            Sleeper.until_file_is_available(PATH_TO_SIMULATION_RESULT, timeout=0.02)
            mock_sleep.assert_called_with(0.01)

    def test_sleep_until_file_is_available_PermissionError(self):
        with (
                patch(MOCK_STRINGS["open"], mock_open(read_data="")) as mock_open_file,
                patch(MOCK_STRINGS["sleep"]) as mock_sleep,
                self.assertRaises(CustomTimeoutError)):
            mock_open_file.side_effect = PermissionError
            Sleeper.until_file_is_available(PATH_TO_SIMULATION_RESULT, timeout=0.02)
            mock_sleep.assert_called_with(0.01)

    def test_sleep_until_file_is_available_no_errors(self):
        with (
                patch(MOCK_STRINGS["open"], mock_open(read_data="")) as mock_open_file,
                patch(MOCK_STRINGS["sleep"]) as mock_sleep):
            Sleeper.until_file_is_available(PATH_TO_SIMULATION_RESULT)
            mock_open_file.assert_called_once_with(PATH_TO_SIMULATION_RESULT)
            mock_sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
