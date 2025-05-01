import time
from collections.abc import Callable
from pathlib import Path

from globals.errors import CustomTimeoutError


class Sleeper:

    @staticmethod
    def until_true(function: Callable, tick: float = 0.01, timeout: float = 5) -> None:
        """
        Sleeps until a function returns True, checking it at fixed intervals, with a
        timeout.

        Args:
            function (Callable): Function to evaluate at every interval.
            tick (float, optional): Interval between checks, in seconds. Defaults to 0.01.
            timeout (float, optional): Timeout after which an exception is thrown, in
                seconds. Defaults to 5.

        Raises:
            CustomTimeoutError: If timeout is reached before the function returns True.
        """
        start_time = time.perf_counter()
        while not function():
            if (time.perf_counter() - start_time) >= timeout:
                raise CustomTimeoutError(timeout)
            time.sleep(tick)

    @staticmethod
    def until_file_is_available(
            file_path: Path, tick: float = 0.01, timeout: float = 0.5) -> None:
        """
        Sleeps until the specified file no longer raises errors when opened, with a timeout.

        Args:
            file_path (Path): Path to the file to be checked.
            tick (float, optional): Time, in seconds, to wait between checks. Defaults
                to 0.01.
            timeout (float, optional): Timeout after which an exception is thrown, in
                seconds. Defaults to 0.5.
        """
        start_time = time.perf_counter()
        while True:
            if (time.perf_counter() - start_time) >= timeout:
                raise CustomTimeoutError(timeout)
            try:
                file = open(file_path)
            except (IOError, PermissionError):
                time.sleep(tick)
            else:
                file.close()
                break
