import logging
import time
from pathlib import Path

import pyautogui
import pyperclip

from globals.constants import (
    COEFFICIENT_OF_LOSS_MAX, COEFFICIENT_OF_LOSS_MIN, NETUNO_RESULTS_PATH,
    PATH_TO_LOWER_TANK_RADIO_BUTTON, RAINFALL_SUBSTITUTION_PERCENT_MAX,
    RAINFALL_SUBSTITUTION_PERCENT_MIN)

logger = logging.getLogger("triton")
pyautogui.PAUSE = 0.08


def saturate(value: float, lower_limit: float, upper_limit: float) -> float:
    """
    Saturates a given value between lower and upper limits, inclusive.

    Args:
        value (float): Value to be saturated.
        lower_limit (float): Lower boundary.
        upper_limit (float): Upper boundary.

    Returns:
        float: Value after saturation is applied.
    """
    return min(upper_limit, max(lower_limit, value))


class Mover:
    """
    Automates the movement across the Netuno 4 application, mainly using keyboard presses
    and movements based on known UI elements.
    """

    @staticmethod
    def from_startup_to_file_selection():
        pyautogui.press(["down", "down", "up"])

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
    """
    Automates operations in the Netuno 4 application, using a combinations of movements from
    the `Mover` class and key presses.
    """

    wait: float

    def __init__(self, extra_wait: float) -> None:
        self.wait = extra_wait / 10

    def _select_file_in_explorer(self, file_path: Path) -> None:
        """
        Selects a file in Windows Explorer, by copying and pasting the desired path, then
        pressing 'Enter'.

        Args:
            file_path (Path): Path to the file to be selected in Explorer.
        """
        pyperclip.copy(file_path.resolve())
        logger.debug(f"Selecting file at '{file_path.resolve()}'")
        time.sleep(self.wait)
        pyautogui.keyDown("ctrl")
        pyautogui.press("v")
        pyautogui.keyUp("ctrl")
        pyautogui.press("enter")

    def _type_float_value(self, value: float) -> None:
        """
        Types a value into the focused field, replacing any dots with commas.

        Args:
            value (float): Value to be typed.
        """
        pyautogui.write(str(value).replace(".", ","))

    def _type_date(self, date: str) -> None:
        pyautogui.write(date)

    def _type_initial_run_off(self, initial_run_off: float) -> None:
        self._type_float_value(initial_run_off)

    def _type_catchment_area(self, catchment_area: float) -> None:
        self._type_float_value(catchment_area)

    def _type_lower_tank_capacity(self, capacity: float) -> None:
        self._type_float_value(capacity)

    def _type_water_demand(self, water_demand: float) -> None:
        self._type_float_value(water_demand)

    def _type_number_of_residents(self, amount: int) -> None:
        pyautogui.write(str(amount))

    def _select_coefficient_of_loss(self, value: float) -> None:
        value = saturate(value, COEFFICIENT_OF_LOSS_MIN, COEFFICIENT_OF_LOSS_MAX)
        self._type_float_value(value)

    def _select_rainwater_replacement_option(self, value: int) -> None:
        value = saturate(
            value, RAINFALL_SUBSTITUTION_PERCENT_MIN, RAINFALL_SUBSTITUTION_PERCENT_MAX)
        pyautogui.press("down", value // 10)

    def _set_export_file_path(self, original_file_path: Path) -> Path:
        """
        Defines the export file path and selects it in Explorer.

        Args:
            original_file_path (Path): Path to the original file.

        Returns:
            Path: Path to the export file.
        """
        export_path = Path(
            NETUNO_RESULTS_PATH,
            original_file_path.stem.split(".", 1)[0]
            ).with_suffix(".out.csv")
        self._select_file_in_explorer(export_path)
        return export_path

    def _setup_precipitation_file(self, precipitation_path: Path, date: str) -> None:
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
            inferior_tank_capacity: float) -> None:
        """
        Sets the parameters for the simulation, going field by field and selecting/typing
        the given values.

        Args:
            initial_run_off_disposal (float): Value for initial run off disposal.
            catchment_area (float): Value for catchment area.
            daily_water_demand (float): Value for daily water demand.
            number_of_residents (int): Value for number of residentes.
            rainwater_replacement_percentage (int): Value for rainwater replacement
                percentage.
            coefficient_of_loss (float): Value for coefficient of loss.
            inferior_tank_capacity (float): Value for inferior tank capacity.
        """
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

    def _simulate_and_start_export(self) -> None:
        pyautogui.press("space")
        Mover.from_simulate_to_export_button()
        pyautogui.press("space")

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
        """
        Configures simulation parameters and runs a simulation with the provided file.

        Args:
            precipitation_path (Path): Path to the input file containing precipitation data.
            date (str): Reference date for the file.
            initial_run_off_disposal (float): Value for initial run off disposal.
            catchment_area (float): Value for catchment area.
            daily_water_demand (float): Value for daily water demand.
            number_of_residents (int): Value for number of residentes.
            rainwater_replacement_percentage (int): Value for rainwater replacement
                percentage.
            coefficient_of_loss (float): Value for coefficient of loss.
            inferior_tank_capacity (float): Value for inferior tank capacity.

        Returns:
            Path: Path to the export file containing the simulation results.
        """
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
        """
        Runs a simulation with the provided file, assuming setup was already completed.

        Args:
            precipitation_path (Path): Path to the input file containing precipitation data.
            date (str): Reference date for the file.

        Returns:
            Path: Path to the export file containing the simulation results.
        """
        Mover.from_export_to_file_selection()
        self._setup_precipitation_file(precipitation_path, date)
        Mover.from_date_to_simulate_button()
        self._simulate_and_start_export()
        exported_path = self._set_export_file_path(precipitation_path)
        return exported_path
