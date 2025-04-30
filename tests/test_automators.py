import unittest
from pathlib import Path
from unittest.mock import call, patch

import pyperclip

from agents.automators import Mover, NetunoAutomator, saturate
from globals.constants import NETUNO_RESULTS_PATH, SIMULATION_PARAMETERS

MOCK_PATHS = {
    "press": "pyautogui.press",
    "move_to": "pyautogui.moveTo",
    "hotkey": "pyautogui.hotkey",
    "key_down": "pyautogui.keyDown",
    "key_up": "pyautogui.keyUp",
    "write": "pyautogui.write",
    "left_click": "pyautogui.leftClick",
    "locate_center": "pyautogui.locateCenterOnScreen",
    "select_file": "agents.automators.NetunoAutomator._select_file_in_explorer",
    "mover": "agents.automators.Mover",
    "type_float": "agents.automators.NetunoAutomator._type_float_value",
    "setup_precipitation": "agents.automators.NetunoAutomator._setup_precipitation_file",
    "set_simulation": "agents.automators.NetunoAutomator._set_simulation_parameters",
    "simulate_export": "agents.automators.NetunoAutomator._simulate_and_start_export",
    "sleep": "time.sleep",
}


class TestSaturation(unittest.TestCase):

    def test_saturate_lower_limit(self):
        self.assertEqual(saturate(50, 100, 200), 100)

    def test_saturate_upper_limit(self):
        self.assertEqual(saturate(50, 0, 10), 10)

    def test_saturate_within_limits(self):
        self.assertEqual(saturate(50, 0, 100), 50)


class TestMover(unittest.TestCase):

    def test_startup_to_file_selection(self):
        with patch(MOCK_PATHS["press"]) as press_mock:
            Mover.from_startup_to_file_selection()
            press_mock.assert_called_once_with(["down", "down", "up"])

    def test_file_selection_to_date(self):
        with patch(MOCK_PATHS["press"]) as press_mock:
            Mover.from_file_selection_to_date()
            press_mock.assert_called_once_with("down", 2)

    def test_date_to_run_off(self):
        with patch(MOCK_PATHS["press"]) as press_mock:
            Mover.from_date_to_initial_run_off_field()
            press_mock.assert_called_once_with("down")

    def test_run_off_to_catchment(self):
        with patch(MOCK_PATHS["press"]) as press_mock:
            Mover.from_initial_run_off_to_catchment_area_field()
            press_mock.assert_called_once_with("tab")

    def test_catchment_to_demand(self):
        with patch(MOCK_PATHS["press"]) as press_mock:
            Mover.from_catchment_area_to_water_demand_field()
            press_mock.assert_called_once_with("tab")

    def test_demand_to_residents(self):
        with patch(MOCK_PATHS["press"]) as press_mock:
            Mover.from_water_demand_to_residents_field()
            press_mock.assert_called_once_with("tab", 2)

    def test_residents_to_replacement(self):
        with patch(MOCK_PATHS["press"]) as press_mock:
            Mover.from_residents_to_rainwater_replacement()
            press_mock.assert_called_once_with("tab", 2)

    def test_replacement_to_loss(self):
        with patch(MOCK_PATHS["press"]) as press_mock:
            Mover.from_rainwater_replacement_to_coefficient_of_loss()
            press_mock.assert_called_once_with("tab")

    def test_to_lower_tank_button(self):
        EXPECTED_CALL_ARGS = (12, 31)
        with (
                patch(MOCK_PATHS["locate_center"]) as locate_mock,
                patch(MOCK_PATHS["move_to"]) as move_mock):
            locate_mock.return_value = EXPECTED_CALL_ARGS
            Mover.to_lower_tank_radio_button()
            locate_mock.assert_called_once()
            move_mock.assert_called_once_with(EXPECTED_CALL_ARGS)

    def test_tank_to_simulate(self):
        with patch(MOCK_PATHS["press"]) as press_mock:
            Mover.from_lower_tank_field_to_simulate_button()
            press_mock.assert_called_once_with("tab")

    def test_simulate_to_export(self):
        with patch(MOCK_PATHS["press"]) as press_mock:
            Mover.from_simulate_to_export_button()
            press_mock.assert_called_once_with("tab")

    def test_date_to_simulate(self):
        with patch(MOCK_PATHS["press"]) as press_mock:
            Mover.from_date_to_simulate_button()
            press_mock.assert_called_once_with("tab", 15)

    def test_export_to_file_selection(self):
        with patch(MOCK_PATHS["press"]) as press_mock:
            Mover.from_export_to_file_selection()
            press_mock.assert_has_calls([call("tab", 5), call("up", 3)])


class TestNetunoAutomator(unittest.TestCase):

    def setUp(self):
        self.automator = NetunoAutomator()

    def test_select_file(self):
        path = Path()
        with (
                patch(MOCK_PATHS["press"]) as press_mock,
                patch(MOCK_PATHS["key_down"]) as keydown_mock,
                patch(MOCK_PATHS["key_up"]) as keyup_mock,
                patch(MOCK_PATHS["sleep"]) as sleep_mock):
            self.automator._select_file_in_explorer(path)
            keydown_mock.assert_called_once_with("ctrl")
            keyup_mock.assert_called_once_with("ctrl")
            sleep_mock.assert_called_once()
            press_mock.assert_has_calls([call("v"), call("enter")])
        self.assertEqual(Path(pyperclip.paste()), path.resolve())

    def test_type_float_value(self):
        with patch(MOCK_PATHS["write"]) as write_mock:
            self.automator._type_float_value(1000.789)
            write_mock.assert_called_once_with("1000,789")

    def test_type_date(self):
        REFERENCE_DATE = "12/12/2012"
        with patch(MOCK_PATHS["write"]) as write_mock:
            self.automator._type_date(REFERENCE_DATE)
            write_mock.assert_called_once_with(REFERENCE_DATE)

    def test_type_residents(self):
        with patch(MOCK_PATHS["write"]) as write_mock:
            self.automator._type_number_of_residents(1234)
            write_mock.assert_called_once_with("1234")

    def test_select_coefficient_of_loss(self):
        with patch(MOCK_PATHS["write"]) as write_mock:
            self.automator._select_coefficient_of_loss(1.5)
            write_mock.assert_called_once_with("1,0")

    def test_select_rainwater_replacement(self):
        with patch(MOCK_PATHS["press"]) as press_mock:
            self.automator._select_rainwater_replacement_option(150)
            press_mock.assert_called_once_with("down", 10)

    def test_set_export_path(self):
        EXPECTED_RESULT = Path(NETUNO_RESULTS_PATH, "sample.out.csv")
        path = Path("sample.something")
        with patch(MOCK_PATHS["select_file"]), patch(MOCK_PATHS["hotkey"]):
            result = self.automator._set_export_file_path(path)
        self.assertEqual(EXPECTED_RESULT, result)

    def test_setup_precipitation_file(self):
        path = Path()
        REFERENCE_DATE = "12/12/2012"
        with (
                patch(MOCK_PATHS["press"]) as press_mock,
                patch(MOCK_PATHS["write"]) as write_mock,
                patch(MOCK_PATHS["key_down"]),
                patch(MOCK_PATHS["key_up"])):
            self.automator._setup_precipitation_file(path, REFERENCE_DATE)
            press_mock.assert_has_calls([
                call(["down", "down", "up"]),
                call("v"),
                call("enter"),
                call("down", 2)])
            write_mock.assert_called_once_with(REFERENCE_DATE)
        self.assertEqual(Path(pyperclip.paste()), path.resolve())

    def test_set_simulation_parameters(self):
        with (
                patch(MOCK_PATHS["mover"]) as mover_mock,
                patch(MOCK_PATHS["type_float"]) as type_float_mock,
                patch(MOCK_PATHS["left_click"]) as click_mock,
                patch(MOCK_PATHS["write"]) as write_mock,
                patch(MOCK_PATHS["press"]) as press_mock):
            self.automator._set_simulation_parameters(**SIMULATION_PARAMETERS)
            mover_mock.from_date_to_initial_run_off_field.assert_called_once()
            type_float_mock.assert_has_calls([
                call(SIMULATION_PARAMETERS["initial_run_off_disposal"]),
                call(SIMULATION_PARAMETERS["catchment_area"]),
                call(SIMULATION_PARAMETERS["daily_water_demand"]),
                call(SIMULATION_PARAMETERS["coefficient_of_loss"]),
                call(SIMULATION_PARAMETERS["inferior_tank_capacity"]),
                ])
            write_mock.assert_called_once_with(
                str(SIMULATION_PARAMETERS["number_of_residents"]))
            click_mock.assert_called_once()
            press_mock.assert_called_once_with(
                "down", SIMULATION_PARAMETERS["rainwater_replacement_percentage"] // 10)
            mover_mock.from_initial_run_off_to_catchment_area_field.assert_called_once()
            mover_mock.from_catchment_area_to_water_demand_field.assert_called_once()
            mover_mock.from_water_demand_to_residents_field.assert_called_once()
            mover_mock.from_residents_to_rainwater_replacement.assert_called_once()
            mover_mock.to_lower_tank_radio_button.assert_called_once()
            mover_mock.from_rainwater_replacement_to_coefficient_of_loss.assert_called_once(
                )

    def test_simulate_and_start(self):
        with (
                patch(MOCK_PATHS["mover"]) as mover_mock,
                patch(MOCK_PATHS["press"]) as press_mock):
            self.automator._simulate_and_start_export()
            mover_mock.from_simulate_to_export_button.assert_called_once()
            press_mock.assert_has_calls([call("space"), call("space")])

    def test_run_first_simulation(self):
        path = Path("test.something")
        REFERENCE_DATE = "12/12/2012"
        EXPECTED_PATH = Path(NETUNO_RESULTS_PATH, "test.out.csv")
        with (
                patch(MOCK_PATHS["setup_precipitation"]) as setup_mock,
                patch(MOCK_PATHS["set_simulation"]) as sim_mock,
                patch(MOCK_PATHS["mover"]) as mover_mock,
                patch(MOCK_PATHS["simulate_export"]) as export_mock,
                patch(MOCK_PATHS["select_file"]) as file_mock):
            result = self.automator.run_first_simulation(
                path, REFERENCE_DATE, **SIMULATION_PARAMETERS)
            setup_mock.assert_called_once_with(path, REFERENCE_DATE)
            sim_mock.assert_called_once_with(*SIMULATION_PARAMETERS.values())
            mover_mock.from_lower_tank_field_to_simulate_button.assert_called_once()
            export_mock.assert_called_once()
            file_mock.assert_called_once_with(EXPECTED_PATH)
        self.assertEqual(result, EXPECTED_PATH)

    def test_run_simulation(self):
        path = Path("test.something")
        REFERENCE_DATE = "12/12/2012"
        EXPECTED_PATH = Path(NETUNO_RESULTS_PATH, "test.out.csv")
        with (
                patch(MOCK_PATHS["setup_precipitation"]) as setup_mock,
                patch(MOCK_PATHS["set_simulation"]) as _,
                patch(MOCK_PATHS["mover"]) as mover_mock,
                patch(MOCK_PATHS["simulate_export"]) as export_mock,
                patch(MOCK_PATHS["select_file"]) as file_mock):
            result = self.automator.run_simulation(path, REFERENCE_DATE)
            mover_mock.from_export_to_file_selection.assert_called_once()
            setup_mock.assert_called_once_with(path, REFERENCE_DATE)
            mover_mock.from_date_to_simulate_button.assert_called_once()
            export_mock.assert_called_once()
            file_mock.assert_called_once_with(EXPECTED_PATH)
        self.assertEqual(result, EXPECTED_PATH)


if __name__ == '__main__':
    unittest.main()
