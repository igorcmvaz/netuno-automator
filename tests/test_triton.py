import logging
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from agents.validators import CommandLineArgsValidator
from agents.manager import ProcessManager
from tests.test_parsers import PATH_TO_SIMULATION_RESULT
from triton import main, setup_logger

MOCK_STRINGS = {
    "popen": "subprocess.Popen",
    "sleep": "time.sleep",
    "run_first": "agents.automators.NetunoAutomator.run_first_simulation",
    "run_simulation": "agents.automators.NetunoAutomator.run_simulation",
    "sleep_until": "agents.sleeper.Sleeper.until_true",
    "base_file_name": "agents.exporter.CSVExporter._get_base_file_name",
}


class TestLoggerSetup(unittest.TestCase):

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


class TestMainFunction(unittest.TestCase):

    def setUp(self):
        self.SAMPLE_FILE_NAME = "test-consolidated.csv"
        self.SAMPLE_RESULTS_FILE = Path(__file__).parent.parent / self.SAMPLE_FILE_NAME
        self.args = CommandLineArgsValidator()
        self.args.netuno_exe_path = Path(__file__).parent / "netuno.exe"
        self.args.precipitation_dir_path = Path(__file__).parent.parent / "example"
        self.args.quiet = 0
        self.args.verbose = True
        self.args.wait = 0
        self.args.clean = False
        self.args.save_every = 10
        self.args.restart_every = 15

    def test_main_no_restart(self):
        self.args.save_every = 2
        self.args.clean = True
        self.args.restart_every = 15
        with (
                patch(MOCK_STRINGS["run_first"]) as mock_first_simulation,
                patch(MOCK_STRINGS["run_simulation"]) as mock_run_simulation,
                patch(MOCK_STRINGS["base_file_name"]) as mock_base_file_name,
                patch(MOCK_STRINGS["sleep"]),
                patch(MOCK_STRINGS["sleep_until"])):
            mock_first_simulation.return_value = PATH_TO_SIMULATION_RESULT
            mock_run_simulation.return_value = PATH_TO_SIMULATION_RESULT
            mock_base_file_name.return_value = self.SAMPLE_FILE_NAME
            main(self.args, ProcessManager())
            mock_first_simulation.assert_called_once()
            self.assertEqual(mock_run_simulation.call_count, 4)

    def test_main_with_restart(self):
        file_count = len(list(self.args.precipitation_dir_path.iterdir()))
        self.args.save_every = file_count
        self.args.clean = False
        self.args.restart_every = file_count - 2

        first_process = MagicMock()
        first_process.pid = 1234
        manager = ProcessManager()
        manager.current_process = first_process

        with (
                patch(MOCK_STRINGS["run_first"]) as mock_first_simulation,
                patch(MOCK_STRINGS["run_simulation"]) as mock_run_simulation,
                patch(MOCK_STRINGS["base_file_name"]) as mock_base_file_name,
                patch(MOCK_STRINGS["popen"]) as popen_mock,
                patch(MOCK_STRINGS["sleep"]),
                patch(MOCK_STRINGS["sleep_until"])):
            popen_mock.return_value = first_process
            mock_first_simulation.return_value = PATH_TO_SIMULATION_RESULT
            mock_run_simulation.return_value = PATH_TO_SIMULATION_RESULT
            mock_base_file_name.return_value = self.SAMPLE_FILE_NAME
            main(self.args, manager)
            self.assertEqual(popen_mock.call_count, 1)
            self.assertEqual(mock_first_simulation.call_count, 2)
            self.assertEqual(mock_run_simulation.call_count, file_count - 2)

    def tearDown(self):
        self.SAMPLE_RESULTS_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
