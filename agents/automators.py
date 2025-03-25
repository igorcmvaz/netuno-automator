import logging
import time
from pathlib import Path

import pyautogui
import pyperclip

from globals.constants import (
    PAUSE, PATH_TO_LOWER_TANK_RADIO_BUTTON, COEFFICIENT_OF_LOSS_MAX,
    COEFFICIENT_OF_LOSS_MIN, RAINFALL_SUBSTITUTION_PERCENT_MAX,
    RAINFALL_SUBSTITUTION_PERCENT_MIN)

logger = logging.getLogger("triton")


def saturate(value: float, lower_limit: float, upper_limit: float) -> float:
    return min(upper_limit, max(lower_limit, value))


class Mover:

    @staticmethod
    def from_startup_to_file_selection():
        pyautogui.press("down", 2)
        time.sleep(PAUSE)
        pyautogui.press("up")

    @staticmethod
    def from_file_selection_to_date():
        pyautogui.press("down", 2)

    @staticmethod
    def from_date_to_initial_run_off_field():
        pyautogui.press("down")

    @staticmethod
    def from_initial_run_off_to_catchment_area_field():
        pyautogui.press("tab")

    @staticmethod
    def from_catchment_area_to_water_demand_field():
        pyautogui.press("tab")

    @staticmethod
    def from_water_demand_to_residents_field():
        pyautogui.press("tab", 2)

    @staticmethod
    def from_residents_to_rainwater_replacement():
        pyautogui.press("tab", 2)

    @staticmethod
    def from_rainwater_replacement_to_coefficient_of_loss():
        pyautogui.press("tab")

    @staticmethod
    def to_lower_tank_radio_button():
        pyautogui.moveTo(pyautogui.locateCenterOnScreen(
            PATH_TO_LOWER_TANK_RADIO_BUTTON, grayscale=True, confidence=0.9))

    @staticmethod
    def from_lower_tank_field_to_simulate_button():
        pyautogui.press("tab")

    @staticmethod
    def from_simulate_to_export_button():
        pyautogui.press("tab")

    @staticmethod
    def from_date_to_simulate_button():
        pyautogui.press("tab", 15)

    @staticmethod
    def from_export_to_file_selection():
        pyautogui.press("tab", 5)
        pyautogui.press("up", 3)


class NetunoAutomator:

    pause: float = 0.8

    def _select_file_in_explorer(self, file_path: Path):
        pyperclip.copy(file_path.resolve())
        logger.info(f"Got path: {file_path.resolve()}")
        time.sleep(self.pause)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(self.pause)
        pyautogui.press("enter")

    def _type_date(self, date: str):
        pyautogui.write(date)

    def _type_initial_run_off(self, initial_run_off: float):
        pyautogui.write(str(initial_run_off).replace(".", ","))

    def _type_catchment_area(self, catchment_area: float):
        pyautogui.write(str(catchment_area).replace(".", ","))

    def _type_lower_tank_capacity(self, capacity: float):
        pyautogui.write(str(capacity).replace(".", ","))

    def _type_water_demand(self, water_demand: float):
        pyautogui.write(str(water_demand).replace(".", ","))

    def _type_number_of_residents(self, amount: int):
        pyautogui.write(str(amount))

    def _select_coefficient_of_loss(self, value: float):
        value = saturate(value, COEFFICIENT_OF_LOSS_MIN, COEFFICIENT_OF_LOSS_MAX)
        pyautogui.write(str(value).replace(".", ","))

    def _select_rainwater_replacement_option(self, value: int):
        value = saturate(
            value, RAINFALL_SUBSTITUTION_PERCENT_MIN, RAINFALL_SUBSTITUTION_PERCENT_MAX)
        pyautogui.press("down", value // 10)

    def _set_export_file_path(self, original_file_path: Path) -> Path:
        export_path = Path(original_file_path.stem.split(".", 1)[0]).with_suffix(".out.csv")
        self._select_file_in_explorer(export_path)
        return export_path

    def _setup_precipitation_file(self, precipitation_path: Path, date: str):
        Mover.from_startup_to_file_selection()
        self._select_file_in_explorer(precipitation_path)
        Mover.from_file_selection_to_date()
        self._type_date(date)

    def _set_simulation_parameters(
            self,
            initial_run_off_disposal: float,
            catchment_area: float,
            daily_water_demand: float,
            number_of_residents: int,
            rainwater_replacement_percentage: int,
            coefficient_of_loss: float,
            inferior_tank_capacity: float):
        Mover.from_date_to_initial_run_off_field()
        self._type_initial_run_off(initial_run_off_disposal)
        Mover.from_initial_run_off_to_catchment_area_field()
        self._type_catchment_area(catchment_area)
        Mover.from_catchment_area_to_water_demand_field()
        self._type_water_demand(daily_water_demand)
        Mover.from_water_demand_to_residents_field()
        self._type_number_of_residents(number_of_residents)
        Mover.from_residents_to_rainwater_replacement()
        self._select_rainwater_replacement_option(rainwater_replacement_percentage)
        Mover.from_rainwater_replacement_to_coefficient_of_loss()
        self._select_coefficient_of_loss(coefficient_of_loss)
        Mover.to_lower_tank_radio_button()
        pyautogui.leftClick()
        self._type_lower_tank_capacity(inferior_tank_capacity)

    def _simulate_and_start_export(self):
        pyautogui.press("space")
        Mover.from_simulate_to_export_button()
        pyautogui.press("space")
        time.sleep(self.pause)

    def run_first_simulation(
            self,
            precipitation_path: Path,
            date: str,
            initial_run_off_disposal: float,
            catchment_area: float,
            daily_water_demand: float,
            number_of_residents: int,
            rainwater_replacement_percentage: int,
            coefficient_of_loss: float,
            inferior_tank_capacity: float) -> Path:
        self._setup_precipitation_file(precipitation_path, date)
        self._set_simulation_parameters(
            initial_run_off_disposal,
            catchment_area,
            daily_water_demand,
            number_of_residents,
            rainwater_replacement_percentage,
            coefficient_of_loss,
            inferior_tank_capacity)
        Mover.from_lower_tank_field_to_simulate_button()
        self._simulate_and_start_export()
        exported_path = self._set_export_file_path(precipitation_path)
        return exported_path

    def run_simulation(self, precipitation_path: Path, date: str) -> Path:
        Mover.from_export_to_file_selection()
        self._setup_precipitation_file(precipitation_path, date)
        Mover.from_date_to_simulate_button()
        self._simulate_and_start_export()
        exported_path = self._set_export_file_path(precipitation_path)
        return exported_path
