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

    def _float_from_string(self, value: str) -> float:
        """
        Converts a string value to a float, considering it might contain dots as thousands
        separators and commas as a decimal separator.

        Args:
            value (str): Value to be converted.

        Returns:
            float: Float value obtained from the conversion.
        """
        return float(value.replace(".", "").replace(",", "."))

    def _get_results(self) -> list[dict[str, str | float]]:
        results = []
        with open(
                self.results_file,
                newline="",
                encoding=SIMULATION_OUTPUT_ATTRIBUTES["encoding"]) as csv_file:
            reader = csv.reader(
                csv_file, delimiter=SIMULATION_OUTPUT_ATTRIBUTES["delimiter"])
            results_section = False
            for index, row in enumerate(reader):
                if SIMULATION_OUTPUT_ATTRIBUTES["start_of_results_label"] in row:
                    results_section = True
                    continue
                if results_section:
                    results.append({
                        "label": row[0],
                        "value": self._float_from_string(row[1])
                    })
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

    def to_list(self, city: str, model: str, scenario: str,) -> list[ResultTuple]:
        """
        Converts the results from `parse_results()` into a list of tuples, each one
        containing a single metric and the corresponding city, model and scenario.

        Args:
            city (str): City corresponding to the results.
            model (str): Model corresponding to the results.
            scenario (str): Scenario corresponding to the results.

        Returns:
            list[ResultTuple]: List of tuples, each one with one metric and identified by
            name of the city, model and scenario.
        """
        content = []
        for metric, variable in self.parse_results().items():
            content.append((
                city,
                model,
                scenario,
                metric,
                variable.label,
                variable.value,
                variable.unit))
        return content
