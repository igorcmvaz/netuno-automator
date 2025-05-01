import logging
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from agents.manager import ProcessManager, logger

MOCK_STRINGS = {
    "popen": "subprocess.Popen",
    "sleep": "time.sleep",
}


class TestProcessManager(unittest.TestCase):

    def test_initialize_manager(self):
        manager = ProcessManager(2)
        self.assertEqual(manager.wait_after_start, 2)
        self.assertIsNone(manager.current_process)

    def test_run_netuno(self):
        manager = ProcessManager(5)
        path = Path(__file__).parent / "netuno.exe"
        new_process = MagicMock()
        new_process.pid = 1234
        EXPECTED_LOG_MESSAGE = "Successfully spawned new process #1234 with Netuno 4"
        with (
                patch(MOCK_STRINGS["popen"]) as popen_mock,
                patch(MOCK_STRINGS["sleep"]) as sleep_mock,
                self.assertLogs(logger, level=logging.DEBUG) as log_context):
            popen_mock.return_value = new_process
            result = manager.run_netuno(path)

            popen_mock.assert_called_once_with(args=(path,))
            self.assertIn(EXPECTED_LOG_MESSAGE, log_context.output[0])
            sleep_mock.assert_called_once_with(5)
        self.assertEqual(result, new_process)

    def test_restart_netuno(self):
        path = Path(__file__).parent / "netuno.exe"
        manager = ProcessManager(5)
        first_process = MagicMock()
        first_process.pid = 1234
        manager.current_process = first_process

        second_process = MagicMock()
        second_process.pid = 5678

        EXPECTED_LOG_MESSAGES = [
            "Successfully spawned new process #1234 with Netuno 4",
            "Terminating Netuno process #1234",
            "Successfully spawned new process #5678 with Netuno 4",
        ]
        with (
                patch(MOCK_STRINGS["popen"]) as popen_mock,
                patch(MOCK_STRINGS["sleep"]) as sleep_mock,
                self.assertLogs(logger, level=logging.DEBUG) as log_context):
            popen_mock.side_effect = [first_process, second_process]
            manager.run_netuno(path)
            popen_mock.assert_called_once_with(args=(path,))

            self.assertIn(EXPECTED_LOG_MESSAGES[0], log_context.output[0])
            sleep_mock.assert_called_once_with(5)

            manager.restart_netuno()
            popen_mock.assert_has_calls([call(args=(path,))])
            self.assertIn(EXPECTED_LOG_MESSAGES[1], log_context.output[1])
            self.assertIn(EXPECTED_LOG_MESSAGES[2], log_context.output[2])

        self.assertEqual(manager.current_process, second_process)


if __name__ == "__main__":
    unittest.main()
