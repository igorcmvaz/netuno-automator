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


class CustomTimeoutError(Exception):
    def __init__(self, timeout: int, *args):
        message = f"Timeout of {timeout} seconds reached"
        super().__init__(message, *args)


class InvalidWaitAttributeError(Exception):
    def __init__(self, wait: float, *args):
        message = f"Provided value {wait} cannot be negative"
        super().__init__(message, *args)


class InvalidRestartAttributeError(Exception):
    def __init__(self, restart_every: int, *args):
        message = f"Provided value {restart_every} is not greater than 0"
        super().__init__(message, *args)
