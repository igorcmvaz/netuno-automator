import logging
import shutil
import unittest
from pathlib import Path

from agents.declutter import Declutter, logger
from globals.constants import NETUNO_RESULTS_PATH

MOCK_STRINGS = {
    "popen": "subprocess.Popen",
    "sleep": "time.sleep",
    "run_first": "agents.automators.NetunoAutomator.run_first_simulation",
    "run_simulation": "agents.automators.NetunoAutomator.run_simulation",
    "sleep_until": "agents.sleeper.Sleeper.until_true",
    "base_file_name": "agents.exporter.CSVExporter._get_base_file_name",
    "path_unlink": "pathlib.Path.unlink",
}


class TestDeclutter(unittest.TestCase):

    def setUp(self):
        self.sample_path = Path(__file__).parent / "declutter"
        self.sample_path.mkdir(exist_ok=True)

    def test_initialization(self):
        path = Path("sample")
        declutter = Declutter(path)
        self.assertEqual(declutter.results_path, path)

    def test_clear_results_files_when_empty(self):
        declutter = Declutter(self.sample_path)
        with self.assertNoLogs(logger, level=logging.DEBUG):
            self.assertFalse(declutter.clear_results_files())

    def test_clear_results_files_when_populated(self):
        declutter = Declutter(self.sample_path)
        new_file = self.sample_path / "test_file.csv"
        new_file.touch()
        EXPECTED_LOG_MESSAGE = (
            f"Deleted 1 results file(s) at '{self.sample_path.resolve()}'")

        with self.assertLogs(logger, level=logging.DEBUG) as log_context:
            self.assertTrue(declutter.clear_results_files())
            self.assertIn(EXPECTED_LOG_MESSAGE, log_context.output[0])

    def test_remove_results_dir_success(self):
        NETUNO_RESULTS_PATH.mkdir(exist_ok=True)
        EXPECTED_LOG_MESSAGE = (
            f"Successfully deleted Netuno results directory at "
            f"'{NETUNO_RESULTS_PATH.resolve()}")

        with self.assertLogs(logger, level=logging.INFO) as log_context:
            Declutter.remove_results_dir()
            self.assertIn(EXPECTED_LOG_MESSAGE, log_context.output[0])

    def test_remove_results_dir_failure(self):
        NETUNO_RESULTS_PATH.mkdir(exist_ok=True)
        temp_file = Path(NETUNO_RESULTS_PATH, "test_file.csv")
        temp_file.touch()
        EXPECTED_LOG_MESSAGE = (
            "Could not delete the Netuno results directory, probably due to it not being "
            "empty")

        with self.assertLogs(logger, level=logging.WARNING) as log_context:
            Declutter.remove_results_dir()
            self.assertIn(EXPECTED_LOG_MESSAGE, log_context.output[0])

    def tearDown(self):
        self.sample_path.rmdir()
        shutil.rmtree(NETUNO_RESULTS_PATH, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
