import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

from globals.constants import OUTPUT_COLUMNS
from globals.types import ResultTuple

logger = logging.getLogger("triton")


class CSVExporter:

    output_path: Path
    content: list[ResultTuple]

    def __init__(self, parent_output_dir: Path):
        self.output_path = Path(parent_output_dir, self._get_base_file_name())
        self.content = []

    def _get_base_file_name(self) -> str:
        """
        Retrieves the base file name for new CSV files.

        Returns:
            str: Base name for new files.
        """
        return f"{datetime.now().strftime('%Y-%m-%dT%H-%M')}-consolidated.csv"

    def add_results(self, result: list[ResultTuple]) -> None:
        """
        Includes the provided results in the next batch that will be saved.

        Args:
            result (list[ResultTuple]): List of results to be included.
        """
        self.content.extend(result)

    def save_results(self) -> None:
        """
        Saves the current batch of results (if any) to the output file,
        then resets the batch.
        """
        if not self.content:
            logger.warning("No new results to save")
            return
        include_header = not self.output_path.is_file()
        pd.DataFrame(self.content, columns=OUTPUT_COLUMNS).to_csv(
            self.output_path, sep=",", index=False, header=include_header, mode="a")
        self.content = []
