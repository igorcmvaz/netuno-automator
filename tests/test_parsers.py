import unittest
from pathlib import Path

from agents.parsers import FileNameParser, ResultParser
from globals.types import Variable

PATH_TO_SIMULATION_RESULT = Path(Path(__file__).parent, "samples", "simulation_result.csv")
PARSED_SAMPLE = [
    {
        "label": "Potencial de economia (%)",
        "value": 9.20
    },
    {
        "label": "Volume consumido médio de água pluvial (litros/dia)",
        "value": 55.4734
    },
    {
        "label": "Volume consumido médio de água potável (litros/dia)",
        "value": 547.527
    },
    {
        "label": "Volume médio de água pluvial extravasado (litros/dia)",
        "value": 136.911
    },
    {
        "label": "Dias em que a demanda de água pluvial é atendida completamente",
        "value": 0.00
    },
    {
        "label": "Dias em que a demanda de água pluvial é atendida parcialmente (%)",
        "value": 39.04
    },
    {
        "label": "Dias em que a demanda de água pluvial não é atendida (%)",
        "value": 60.96
    },
]
SAMPLE_RESULTS = {
    "potential_savings": Variable(
        label="Potencial de economia (%)",
        unit="%",
        value=9.2),
    "average_rainwater_consumption": Variable(
        label="Volume consumido médio de água pluvial (litros/dia)",
        unit="liters/day",
        value=55.4734),
    "average_drinking_water_consumption": Variable(
        label="Volume consumido médio de água potável (litros/dia)",
        unit="liters/day",
        value=547.527),
    "average_rainwater_overflow": Variable(
        label="Volume médio de água pluvial extravasado (litros/dia)",
        unit="liters/day",
        value=136.911),
    "period_when_demand_is_fully_met": Variable(
        label="Dias em que a demanda de água pluvial é atendida completamente",
        unit="days",
        value=0),
    "period_when_demand_is_partially_met": Variable(
        label="Dias em que a demanda de água pluvial é atendida parcialmente (%)",
        unit="%",
        value=39.04),
    "period_when_demand_is_not_met": Variable(
        label="Dias em que a demanda de água pluvial não é atendida (%)",
        unit="%",
        value=60.96),
}


class TestFileNameParser(unittest.TestCase):

    def test_get_metadata_historic_no_prefix(self):
        FILE_NAME = Path(__file__).parent / "Curitiba_ACCESS-CM2_Histórico.csv"
        result = FileNameParser.get_metadata(FILE_NAME)
        self.assertTupleEqual(result, ("Curitiba", "ACCESS-CM2", "Histórico"))

    def test_get_metadata_historic_with_prefix(self):
        FILE_NAME = Path(__file__).parent / "(Netuno)Curitiba_ACCESS-CM2_Histórico.csv"
        result = FileNameParser.get_metadata(FILE_NAME)
        self.assertTupleEqual(result, ("Curitiba", "ACCESS-CM2", "Histórico"))

    def test_get_metadata_ssp_no_prefix(self):
        FILE_NAME = Path(__file__).parent / "Curitiba_ACCESS-CM2_SSP245.csv"
        result = FileNameParser.get_metadata(FILE_NAME)
        self.assertTupleEqual(result, ("Curitiba", "ACCESS-CM2", "SSP245"))

    def test_get_metadata_ssp_with_prefix(self):
        FILE_NAME = Path(__file__).parent / "(Netuno)Curitiba_ACCESS-CM2_SSP585.csv"
        result = FileNameParser.get_metadata(FILE_NAME)
        self.assertTupleEqual(result, ("Curitiba", "ACCESS-CM2", "SSP585"))

    def test_get_metadata_city_with_accents(self):
        FILE_NAME = Path(__file__).parent / "Florianópolis_ACCESS-CM2_Histórico.csv"
        result = FileNameParser.get_metadata(FILE_NAME)
        self.assertTupleEqual(result, ("Florianópolis", "ACCESS-CM2", "Histórico"))

    def test_get_metadata_city_with_spaces(self):
        FILE_NAME = Path(__file__).parent / "São Paulo_ACCESS-CM2_Histórico.csv"
        result = FileNameParser.get_metadata(FILE_NAME)
        self.assertTupleEqual(result, ("São Paulo", "ACCESS-CM2", "Histórico"))


class TestResultsParser(unittest.TestCase):

    def setUp(self):
        self.parser = ResultParser(PATH_TO_SIMULATION_RESULT)

    def test_float_from_string(self):
        TEST_SAMPLES = [
            ("3,14", 3.14),
            ("0,14", 0.14),
            ("3,00", 3),
            ("10.553,14", 10553.14),
            ("10.553", 10.553),
            ("0.14", 0.14),
            ]
        for value, expected_value in TEST_SAMPLES:
            with self.subTest(value=value):
                self.assertEqual(self.parser._float_from_string(value), expected_value)

    def test_get_results_from_sample(self):
        actual_results = self.parser._get_results()

        self.assertListEqual(actual_results, PARSED_SAMPLE)

    def test_parse_results_from_sample(self):
        actual_results = self.parser.parse_results()

        self.assertDictEqual(actual_results, SAMPLE_RESULTS)

    def test_results_to_list(self):
        actual_results = self.parser.to_list("Florianópolis", "ACCESS-CM2", "Histórico")
        EXPECTED_RESULT = [
            ("Florianópolis", "ACCESS-CM2", "Histórico",
                "potential_savings", "Potencial de economia (%)", 9.2, "%"),
            ("Florianópolis", "ACCESS-CM2", "Histórico", "average_rainwater_consumption",
             "Volume consumido médio de água pluvial (litros/dia)", 55.4734, "liters/day"),
            ("Florianópolis", "ACCESS-CM2", "Histórico",
             "average_drinking_water_consumption",
             "Volume consumido médio de água potável (litros/dia)", 547.527, "liters/day"),
            ("Florianópolis", "ACCESS-CM2", "Histórico", "average_rainwater_overflow",
             "Volume médio de água pluvial extravasado (litros/dia)", 136.911,
             "liters/day"),
            ("Florianópolis", "ACCESS-CM2", "Histórico", "period_when_demand_is_fully_met",
             "Dias em que a demanda de água pluvial é atendida completamente", 0, "days"),
            ("Florianópolis", "ACCESS-CM2", "Histórico",
             "period_when_demand_is_partially_met",
             "Dias em que a demanda de água pluvial é atendida parcialmente (%)", 39.04,
             "%"),
            ("Florianópolis", "ACCESS-CM2", "Histórico", "period_when_demand_is_not_met",
             "Dias em que a demanda de água pluvial não é atendida (%)", 60.96, "%")
        ]

        self.assertListEqual(actual_results, EXPECTED_RESULT)


if __name__ == '__main__':
    unittest.main()
