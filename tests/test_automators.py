import logging
import unittest
from pathlib import Path
from unittest.mock import patch, call

from agents.automators import Mover, NetunoAutomator, saturate

MOCK_PATHS = {
    "press": "pyautogui.press",
    "sleep": "time.sleep",
    "move_to": "pyautogui.moveTo",
    "locate_center": "pyautogui.locateCenterOnScreen"
}


class TestSaturation(unittest.TestCase):

    def test_saturate_lower_limit(self):
        self.assertEqual(saturate(50, 100, 200), 100)

    def test_saturate_upper_limit(self):
        self.assertEqual(saturate(50, 0, 10), 10)

    def test_saturate_within_limits(self):
        self.assertEqual(saturate(50, 0, 100), 50)


@patch(MOCK_PATHS["sleep"], new=lambda _: None)
class TestMover(unittest.TestCase):

    def test_startup_to_file_selection(self):
        with patch(MOCK_PATHS["press"]) as press_mock:
            Mover.from_startup_to_file_selection()
            press_mock.assert_has_calls([call("down", 2), call("up",)])

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


class TestNetunoAutomator(unittest.TestCase):

    def setUp(self):
        self.automator = NetunoAutomator()

    def test_select_file(self):
        pass

    def test_type_date(self):
        pass

    def test_type_run_off(self):
        pass

    def test_type_catchment_area(self):
        pass

    def test_type_tank_capacity(self):
        pass


if __name__ == '__main__':
    unittest.main()
