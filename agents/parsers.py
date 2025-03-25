import csv
import re
from pathlib import Path

from globals.constants import SIMULATION_OUTPUT_ATTRIBUTES
from globals.types import Variable


class FileNameParser:

    @staticmethod
    def get_metadata(file_name: Path) -> tuple[str, str, str]:
        """
        Parses a file name to retrieve city name and climate model and scenario.

        The expected file name format is:
        `(optional_anything){city_name}_{model}_{scenario}.{extension}`

        NOTE: The underscore is used to separate fields, meaning it is expected to be
        present only at the limits between fields.

        Examples:
            * `(Netuno)Florianópolis_ACCESS-CM2_Histórico.csv`
            * `(Netuno)São Paulo_GFDL-CM4_SSP245.csv`
            * `(Netuno)Rio de Janeiro_MIROC6_SSP585.csv`
            * `Belo Horizonte_TaiESM1_Histórico.csv`
            * `Brasília_GFDL-CM4_SSP245.csv`

        Args:
            file_name (Path): Path to the file whose name should be parsed.

        Returns:
            tuple[str, str, str]: Tuple containing city name, climate model and scenario.
        """
        city, model, scenario = file_name.stem.split(".", 1)[0].split("_")
        if (match := re.search(r"\(.*\)", city)):
            city = city.replace(match.group(), "")
        return city, model, scenario


class ResultParser:

    def __init__(self, results_file: Path):
        self.results_file = results_file

    def _get_results(self) -> list[dict[str, str | float]]:
        results = []
        with open(
                self.results_file,
                newline="",
                encoding=SIMULATION_OUTPUT_ATTRIBUTES["encoding"]) as csv_file:
            reader = csv.reader(
                csv_file, delimiter=SIMULATION_OUTPUT_ATTRIBUTES["delimiter"])
            for index, row in enumerate(reader):
                if index < SIMULATION_OUTPUT_ATTRIBUTES["skip_n_rows"]:
                    continue
                results.append({"label": row[0], "value": float(row[1])})
        return results

    def parse_results(self) -> dict[str, Variable]:
        results = self._get_results()
        return {
            "potential_savings": Variable(
                label=results[0]["label"], unit="%", value=results[0]["value"]),
            "average_rainwater_consumption": Variable(
                label=results[1]["label"], unit="liters/day", value=results[1]["value"]),
            "average_drinking_water_consumption": Variable(
                label=results[2]["label"], unit="liters/day", value=results[2]["value"]),
            "average_rainwater_overflow": Variable(
                label=results[3]["label"], unit="liters/day", value=results[3]["value"]),
            "period_when_demand_is_fully_met": Variable(
                label=results[4]["label"], unit="days", value=results[4]["value"]),
            "period_when_demand_is_partially_met": Variable(
                label=results[5]["label"], unit="%", value=results[5]["value"]),
            "period_when_demand_is_not_met": Variable(
                label=results[6]["label"], unit="%", value=results[6]["value"]),
        }
