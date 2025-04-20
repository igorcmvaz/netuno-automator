import logging
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from agents.validators import CommandLineArgsValidator
from globals.constants import NETUNO_RESULTS_PATH
from tests.test_parsers import PATH_TO_SIMULATION_RESULT
from triton import logger, main, run_netuno, setup_logger, sleep_until

MOCK_STRINGS = {
    "popen": "subprocess.Popen",
    "sleep": "time.sleep",
    "run_first": "agents.automators.NetunoAutomator.run_first_simulation",
    "run_simulation": "agents.automators.NetunoAutomator.run_simulation",
    "sleep_until": "triton.sleep_until",
    "base_file_name": "agents.exporter.CSVExporter._get_base_file_name",
    "rmtree": "shutil.rmtree",
}


class TestHelperFunctions(unittest.TestCase):

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

    def test_sleep_until(self):
        mock_function = MagicMock(side_effect=[False, False, True])

        with patch(MOCK_STRINGS["sleep"]) as mock_sleep:
            sleep_until(mock_function)
            mock_sleep.assert_called_with(0.01)

        self.assertEqual(mock_function.call_count, 3)


class TestMainFunction(unittest.TestCase):

    def test_main(self):
        SAMPLE_FILE_NAME = "test-consolidated.csv"
        SAMPLE_RESULTS_FILE = Path(__file__).parent.parent / SAMPLE_FILE_NAME
        args = CommandLineArgsValidator()
        args.netuno_exe_path = Path(__file__).parent / "netuno.exe"
        args.precipitation_dir_path = Path(__file__).parent.parent / "example"
        args.quiet = 0
        args.verbose = True
        args.clean = True
        args.save_every = 2

        with (
                patch(MOCK_STRINGS["run_first"]) as mock_first_simulation,
                patch(MOCK_STRINGS["run_simulation"]) as mock_run_simulation,
                patch(MOCK_STRINGS["base_file_name"]) as mock_base_file_name,
                patch(MOCK_STRINGS["rmtree"]) as mock_rmtree,
                patch(MOCK_STRINGS["sleep_until"])):
            mock_first_simulation.return_value = PATH_TO_SIMULATION_RESULT
            mock_run_simulation.return_value = PATH_TO_SIMULATION_RESULT
            mock_base_file_name.return_value = SAMPLE_FILE_NAME
            main(args)
            mock_first_simulation.assert_called_once()
            self.assertEqual(mock_run_simulation.call_count, 4)
            mock_rmtree.assert_called_once_with(NETUNO_RESULTS_PATH)
        NETUNO_RESULTS_PATH.rmdir()
        SAMPLE_RESULTS_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
