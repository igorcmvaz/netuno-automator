from pathlib import Path


class InvalidNetunoExecutableError(Exception):
    def __init__(self, path_to_netuno: Path, *args):
        message = f"No file at '{path_to_netuno.resolve()}'"
        super().__init__(message, *args)


class InvalidSourceDirectoryError(Exception):
    def __init__(self, source_directory: Path, *args):
        message = f"Provided path '{source_directory.resolve()}' is not a directory"
        super().__init__(message, *args)


class MissingInputDataError(Exception):
    def __init__(self, source_directory: Path, *args):
        message = f"Provided path '{source_directory.resolve()}' has no CSV files"
        super().__init__(message, *args)


class InvalidPartialSaveAttributeError(Exception):
    def __init__(self, save_every: int, *args):
        message = f"Provided value {save_every} is not greater than 0"
        super().__init__(message, *args)
