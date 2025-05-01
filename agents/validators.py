from pathlib import Path

from globals.errors import (
    InvalidNetunoExecutableError, InvalidPartialSaveAttributeError,
    InvalidRestartAttributeError, InvalidSourceDirectoryError, InvalidWaitAttributeError,
    MissingInputDataError)


class CommandLineArgsValidator:

    netuno_exe_path: Path
    precipitation_dir_path: Path
    quiet: int
    verbose: bool
    clean: bool
    save_every: int
    wait: float
    restart_every: int

    def _validate_netuno_path(self) -> None:
        """
        Validates the path to a Netuno executable file, checking if it actually is a file.

        Raises:
            InvalidNetunoExecutableError: If the given path is not a file.
        """
        if not self.netuno_exe_path.is_file():
            raise InvalidNetunoExecutableError(self.netuno_exe_path)

    def _validate_precipitation_path(self) -> None:
        """
        Validates the path to a directory containing CSV files with precipitation data,
        checking if it actually is a directory and contains at least 1 CSV file.

        Raises:
            InvalidSourceDirectoryError: If the given path is not a directory.
            MissingInputDataError: If the directory contains no CSV files.
        """
        if not self.precipitation_dir_path.is_dir():
            raise InvalidSourceDirectoryError(self.precipitation_dir_path)
        if not any(
                file for file in self.precipitation_dir_path.iterdir()
                if ".csv" == file.suffix.casefold()):
            raise MissingInputDataError(self.precipitation_dir_path)

    def _validate_save_every_n(self) -> None:
        """
        Validates the value of the partial save attribute, which should be greater than 0.

        Raises:
            InvalidPartialSaveAttributeError: If the given value is less than or equal to 0.
        """
        if self.save_every <= 0:
            raise InvalidPartialSaveAttributeError(self.save_every)

    def _validate_wait(self) -> None:
        """
        Validates the value of the wait attribute, which should not be negative.

        Raises:
            InvalidPartialSaveAttributeError: If the given value is less than 0.
        """
        if self.wait < 0:
            raise InvalidWaitAttributeError(self.wait)

    def _validate_restart_every_n(self) -> None:
        """
        Validates the value of the restart every attribute, which should be greater than 0.

        Raises:
            InvalidRestartAttributeError: If the given value is less than or equal to 0.
        """
        if self.restart_every <= 0:
            raise InvalidRestartAttributeError(self.restart_every)

    def validate_arguments(self) -> None:
        """Executes all validation methods from the class."""
        self._validate_netuno_path()
        self._validate_precipitation_path()
        self._validate_save_every_n()
        self._validate_wait()
        self._validate_restart_every_n()
