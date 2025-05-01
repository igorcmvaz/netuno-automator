import logging
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from agents.validators import CommandLineArgsValidator
from globals.errors import CustomTimeoutError
from tests.test_parsers import PATH_TO_SIMULATION_RESULT
from triton import logger, main, restart_netuno, run_netuno, setup_logger, sleep_until

MOCK_STRINGS = {
    "popen": "subprocess.Popen",
    "sleep": "time.sleep",
    "run_first": "agents.automators.NetunoAutomator.run_first_simulation",
    "run_simulation": "agents.automators.NetunoAutomator.run_simulation",
    "sleep_until": "triton.sleep_until",
    "base_file_name": "agents.exporter.CSVExporter._get_base_file_name",
    "path_unlink": "pathlib.Path.unlink",
}


class TestNetunoFunctions(unittest.TestCase):

    def test_run_netuno(self):
        path = Path(__file__).parent / "netuno.exe"
        new_process = MagicMock()
        new_process.pid = 1234
        EXPECTED_LOG_MESSAGE = "Successfully spawned new process #1234 with Netuno 4"
        with (
                patch(MOCK_STRINGS["popen"]) as popen_mock,
                patch(MOCK_STRINGS["sleep"]) as sleep_mock,
                self.assertLogs(logger, level=logging.DEBUG) as log_context):
            popen_mock.return_value = new_process
            result = run_netuno(path, wait_after_start=5)

            popen_mock.assert_called_once_with(args=(path,))
            self.assertIn(EXPECTED_LOG_MESSAGE, log_context.output[0])
            sleep_mock.assert_called_once_with(5)
        self.assertEqual(result, new_process)

    def test_restart_netuno(self):
        path = Path(__file__).parent / "netuno.exe"
        first_process = MagicMock()
        first_process.pid = 1234
        second_process = MagicMock()
        second_process.pid = 5678
        processes = {"netuno": first_process}

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
            run_netuno(path, wait_after_start=5)
            popen_mock.assert_called_once_with(args=(path,))

            self.assertIn(EXPECTED_LOG_MESSAGES[0], log_context.output[0])
            sleep_mock.assert_called_once_with(5)

            restart_netuno(processes, wait_after_start=5)
            popen_mock.assert_has_calls([call(args=(path,))])
            self.assertIn(EXPECTED_LOG_MESSAGES[1], log_context.output[1])
            self.assertIn(EXPECTED_LOG_MESSAGES[2], log_context.output[2])

        self.assertEqual(processes.get("netuno"), second_process)


class TestHelperFunctions(unittest.TestCase):

    def test_setup_logger_verbose(self):
        test_logger = logging.getLogger("test_logger")
        setup_logger(test_logger, verbose=True)

        self.assertEqual(test_logger.level, logging.DEBUG)
        with self.assertLogs(test_logger, level=logging.INFO) as log_context:
            test_logger.info("Test INFO")
            self.assertIn("Test INFO", log_context.output[0])

    def test_setup_logger_default(self):
        test_logger = logging.getLogger("test_logger")
        setup_logger(test_logger)

        self.assertEqual(test_logger.level, logging.INFO)
        with self.assertLogs(test_logger, level=logging.INFO) as log_context:
            test_logger.info("Test INFO")
            self.assertIn("Test INFO", log_context.output[0])

    def test_setup_logger_quiet(self):
        test_logger = logging.getLogger("test_logger")
        setup_logger(test_logger, quiet_count=1)

        self.assertEqual(test_logger.level, logging.WARNING)
        with self.assertLogs(test_logger, level=logging.WARNING) as log_context:
            test_logger.warning("Test WARNING")
            self.assertIn("Test WARNING", log_context.output[0])

    def test_setup_logger_very_quiet(self):
        test_logger = logging.getLogger("test_logger")
        setup_logger(test_logger, quiet_count=2)

        self.assertEqual(test_logger.level, logging.ERROR)
        with self.assertLogs(test_logger, level=logging.CRITICAL) as log_context:
            test_logger.critical("Test CRITICAL")
            self.assertIn("Test CRITICAL", log_context.output[0])

    def test_sleep_until_success(self):
        mock_function = MagicMock(side_effect=[False, False, True])

        with patch(MOCK_STRINGS["sleep"]) as mock_sleep:
            sleep_until(mock_function)
            mock_sleep.assert_called_with(0.01)

        self.assertEqual(mock_function.call_count, 3)

    def test_sleep_until_timeout(self):
        mock_function = MagicMock(return_value=False)

        with patch(MOCK_STRINGS["sleep"]) as mock_sleep:
            with self.assertRaises(CustomTimeoutError):
                sleep_until(mock_function, timeout=0.02)
                mock_sleep.assert_called_with(0.01)


class TestMainFunction(unittest.TestCase):

    def test_main_no_restart(self):
        SAMPLE_FILE_NAME = "test-consolidated.csv"
        SAMPLE_RESULTS_FILE = Path(__file__).parent.parent / SAMPLE_FILE_NAME
        args = CommandLineArgsValidator()
        args.netuno_exe_path = Path(__file__).parent / "netuno.exe"
        args.precipitation_dir_path = Path(__file__).parent.parent / "example"
        args.quiet = 0
        args.verbose = True
        args.clean = True
        args.save_every = 2
        args.restart_every = 15
        args.wait = 0
        netuno_process = MagicMock()
        processes = {"netuno": netuno_process}

        with (
                patch(MOCK_STRINGS["run_first"]) as mock_first_simulation,
                patch(MOCK_STRINGS["run_simulation"]) as mock_run_simulation,
                patch(MOCK_STRINGS["base_file_name"]) as mock_base_file_name,
                patch(MOCK_STRINGS["path_unlink"]) as mock_unlink,
                patch(MOCK_STRINGS["sleep"]),
                patch(MOCK_STRINGS["sleep_until"])):
            mock_first_simulation.return_value = PATH_TO_SIMULATION_RESULT
            mock_run_simulation.return_value = PATH_TO_SIMULATION_RESULT
            mock_base_file_name.return_value = SAMPLE_FILE_NAME
            main(args, processes)
            mock_first_simulation.assert_called_once()
            mock_unlink.assert_called()
            self.assertEqual(mock_run_simulation.call_count, 4)
        SAMPLE_RESULTS_FILE.unlink(missing_ok=True)

    def test_main_with_restart(self):
        SAMPLE_FILE_NAME = "test-consolidated.csv"
        SAMPLE_RESULTS_FILE = Path(__file__).parent.parent / SAMPLE_FILE_NAME
        args = CommandLineArgsValidator()
        args.netuno_exe_path = Path(__file__).parent / "netuno.exe"
        args.precipitation_dir_path = Path(__file__).parent.parent / "example"
        file_count = len(list(args.precipitation_dir_path.iterdir()))
        args.quiet = 0
        args.verbose = True
        args.clean = False
        args.save_every = file_count
        args.restart_every = file_count - 2
        args.wait = 0

        first_process = MagicMock()
        first_process.pid = 1234
        processes = {"netuno": first_process}

        with (
                patch(MOCK_STRINGS["run_first"]) as mock_first_simulation,
                patch(MOCK_STRINGS["run_simulation"]) as mock_run_simulation,
                patch(MOCK_STRINGS["base_file_name"]) as mock_base_file_name,
                patch(MOCK_STRINGS["path_unlink"]) as mock_unlink,
                patch(MOCK_STRINGS["popen"]) as popen_mock,
                patch(MOCK_STRINGS["sleep"]),
                patch(MOCK_STRINGS["sleep_until"])):
            popen_mock.return_value = first_process
            mock_first_simulation.return_value = PATH_TO_SIMULATION_RESULT
            mock_run_simulation.return_value = PATH_TO_SIMULATION_RESULT
            mock_base_file_name.return_value = SAMPLE_FILE_NAME
            main(args, processes)
            self.assertEqual(popen_mock.call_count, 1)
            self.assertEqual(mock_first_simulation.call_count, 2)
            self.assertEqual(mock_run_simulation.call_count, file_count - 2)
            self.assertEqual(mock_unlink.call_count, 0)
        SAMPLE_RESULTS_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
