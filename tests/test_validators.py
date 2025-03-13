import unittest
from pathlib import Path

from agents.validators import CommandLineArgsValidator
from globals.errors import (
    InvalidNetunoExecutableError, InvalidSourceDirectoryError, MissingInputDataError)


class TestCommandLineArgsValidator(unittest.TestCase):

    BASE_PATH = Path(__file__).parent
    NETUNO_PATH = Path(BASE_PATH, "netuno.exe")
    PRECIPITATION_PATH = Path(BASE_PATH, "precipitation")
    CSV_PATH = Path(PRECIPITATION_PATH, "test.csv")

    def setUp(self):
        self.validator = CommandLineArgsValidator()
        self.validator.netuno_exe_path = self.NETUNO_PATH
        self.validator.precipitation_dir_path = self.PRECIPITATION_PATH

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
        with self.assertRaises(InvalidSourceDirectoryError):
            self.validator._validate_precipitation_path()

    def test_validate_precipitation_path_no_csvs(self):
        self.PRECIPITATION_PATH.mkdir()
        alternate_file = Path(self.PRECIPITATION_PATH, "something.ELSE")
        alternate_file.touch()

        with self.assertRaises(MissingInputDataError):
            self.validator._validate_precipitation_path()

        alternate_file.unlink()
        self.PRECIPITATION_PATH.rmdir()

    def test_validate_arguments(self):
        self.PRECIPITATION_PATH.mkdir(exist_ok=True)
        self.NETUNO_PATH.touch(exist_ok=True)
        self.CSV_PATH.touch(exist_ok=True)

        self.assertIsNone(self.validator.validate_arguments())

        self.CSV_PATH.unlink()
        self.NETUNO_PATH.unlink()
        self.PRECIPITATION_PATH.rmdir()


if __name__ == '__main__':
    unittest.main()
