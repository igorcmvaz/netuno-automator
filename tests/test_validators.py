import unittest
from pathlib import Path

from agents.validators import CommandLineArgsValidator
from globals.errors import (
    InvalidNetunoExecutableError, InvalidPartialSaveAttributeError,
    InvalidRestartAttributeError, InvalidSourceDirectoryError, InvalidWaitAttributeError,
    MissingInputDataError)


class TestCommandLineArgsValidator(unittest.TestCase):

    BASE_PATH = Path(__file__).parent
    NETUNO_PATH = Path(BASE_PATH, "netuno.exe")
    PRECIPITATION_PATH = Path(BASE_PATH, "precipitation")
    CSV_PATH = Path(PRECIPITATION_PATH, "test.csv")

    @classmethod
    def setUpClass(cls):
        cls.validator = CommandLineArgsValidator()
        cls.validator.netuno_exe_path = cls.NETUNO_PATH
        cls.validator.precipitation_dir_path = cls.PRECIPITATION_PATH

    def test_validate_netuno_path_success(self):
        self.NETUNO_PATH.touch(exist_ok=True)

        self.assertIsNone(self.validator._validate_netuno_path())

        self.NETUNO_PATH.unlink()

    def test_validate_netuno_path_failure(self):
        self.NETUNO_PATH.unlink(missing_ok=True)

        with self.assertRaises(InvalidNetunoExecutableError):
            self.validator._validate_netuno_path()

    def test_validate_precipitation_path_success(self):
        self.PRECIPITATION_PATH.mkdir()
        self.CSV_PATH.touch()

        self.assertIsNone(self.validator._validate_precipitation_path())

        self.CSV_PATH.unlink()
        self.PRECIPITATION_PATH.rmdir()

    def test_validate_precipitation_path_not_a_dir(self):
        self.CSV_PATH.unlink(missing_ok=True)
        if self.PRECIPITATION_PATH.is_dir():
            self.PRECIPITATION_PATH.rmdir()
        with self.assertRaises(InvalidSourceDirectoryError):
            self.validator._validate_precipitation_path()

    def test_validate_precipitation_path_no_csvs(self):
        self.PRECIPITATION_PATH.mkdir(exist_ok=True)
        alternate_file = Path(self.PRECIPITATION_PATH, "something.ELSE")
        alternate_file.touch()

        with self.assertRaises(MissingInputDataError):
            self.validator._validate_precipitation_path()

        alternate_file.unlink()
        self.PRECIPITATION_PATH.rmdir()

    def test_validate_save_every_n_success(self):
        self.validator.save_every = 5

        self.assertIsNone(self.validator._validate_save_every_n())

    def test_validate_save_every_n_failure(self):
        self.validator.save_every = 0

        with self.assertRaises(InvalidPartialSaveAttributeError):
            self.validator._validate_save_every_n()

    def test_validate_wait_success(self):
        self.validator.wait = 5.0

        self.assertIsNone(self.validator._validate_wait())

    def test_validate_wait_failure(self):
        self.validator.wait = -1.0

        with self.assertRaises(InvalidWaitAttributeError):
            self.validator._validate_wait()

    def test_validate_restart_every_n_success(self):
        self.validator.restart_every = 5

        self.assertIsNone(self.validator._validate_restart_every_n())

    def test_validate_restart_every_n_failure(self):
        self.validator.restart_every = 0

        with self.assertRaises(InvalidRestartAttributeError):
            self.validator._validate_restart_every_n()

    def test_validate_arguments(self):
        self.PRECIPITATION_PATH.mkdir(exist_ok=True)
        self.NETUNO_PATH.touch(exist_ok=True)
        self.CSV_PATH.touch(exist_ok=True)
        self.validator.save_every = 5
        self.validator.wait = 2
        self.validator.restart_every = 5

        self.assertIsNone(self.validator.validate_arguments())

        self.CSV_PATH.unlink()
        self.NETUNO_PATH.unlink()
        self.PRECIPITATION_PATH.rmdir()


if __name__ == '__main__':
    unittest.main()
