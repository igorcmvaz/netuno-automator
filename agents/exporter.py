import json
import logging
from datetime import datetime
from pathlib import Path

from globals.types import SimulationResults, Variable

logger = logging.getLogger("triton")


class Exporter:

    def __init__(self, parent_output_dir: Path):
        self.parent_output_dir = parent_output_dir

    def _get_base_file_name(self) -> str:
        """
        Retrieves the base file name for new JSON files.

        Returns:
            str: Base name for new JSON files.
        """
        return f"{datetime.now().strftime('%Y-%m-%dT%H-%M')}-consolidated.json"

    def save_results(
            self, city_name: str, model: str, scenario: str, results: dict[str, Variable]
            ) -> None:
        # TODO: check output format (list or dictionary? what would be the keys?)
        output_path = Path(self.parent_output_dir, self._get_base_file_name())
        result = SimulationResults(city_name, model, scenario, **results)
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(result, file, ensure_ascii=False, indent=2, default=vars)
        logger.info(f"Successfully exported dataframe to '{output_path.resolve()}'")
