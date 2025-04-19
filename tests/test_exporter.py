import logging
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import time_machine

from agents.exporter import CSVExporter, logger

ZONE_INFO = ZoneInfo("America/Sao_Paulo")


class TestCSVExporter(unittest.TestCase):

    @time_machine.travel(datetime(2020, 11, 5, 23, 45, tzinfo=ZONE_INFO))
    def test_initialization(self):
        path = Path(__file__).parent
        EXPECTED_PATH = Path(path, "2020-11-05T23-45-consolidated.csv")
        exporter = CSVExporter(path)
        self.assertListEqual(exporter.content, [])
        self.assertEqual(exporter.output_path, EXPECTED_PATH)

    @time_machine.travel(datetime(1998, 5, 30, 13, 1, tzinfo=ZONE_INFO))
    def test_get_base_file_name(self):
        exporter = CSVExporter(Path(__file__).parent)
        self.assertEqual(
            exporter._get_base_file_name(), "1998-05-30T13-01-consolidated.csv")

    def test_add_results(self):
        exporter = CSVExporter(Path(__file__).parent)
        RESULTS = [
            ("city", "model", "scenario", "metric", "label", 3.14, "unit"),
            ("city2", "model2", "scenario2", "metric2", "label2", 1.16, "unit2"),
            ("city3", "model3", "scenario3", "metric3", "label3", 6.28, "unit3")]
        exporter.add_results(RESULTS)
        self.assertListEqual(exporter.content, RESULTS)

    def test_save_results_no_content(self):
        EXPECTED_LOG_MESSAGE = "No new results to save"
        exporter = CSVExporter(Path(__file__).parent)
        with self.assertLogs(logger, level=logging.WARNING) as log_context:
            exporter.save_results()
            self.assertIn(EXPECTED_LOG_MESSAGE, log_context.output[0])

    def test_save_results_with_content(self):
        exporter = CSVExporter(Path(__file__).parent)
        exporter.output_path = Path(__file__).parent / "samples" / "test.csv"
        RESULTS = [
            ("city", "model", "scenario", "metric", "label", 3.14, "unit"),
            ("city2", "model2", "scenario2", "metric2", "label2", 1.16, "unit2"),
            ("city3", "model3", "scenario3", "metric3", "label3", 6.28, "unit3")]
        exporter.add_results(RESULTS)
        exporter.save_results()

        self.assertListEqual(exporter.content, [])
        self.assertTrue(exporter.output_path.is_file())
        exporter.output_path.unlink()


if __name__ == '__main__':
    unittest.main()
