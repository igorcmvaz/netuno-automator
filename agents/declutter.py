import logging
from pathlib import Path

from globals.constants import NETUNO_RESULTS_PATH

logger = logging.getLogger("triton")


class Declutter:

    results_path: Path

    def __init__(self, results_path: Path) -> None:
        self.results_path = results_path

    def clear_results_files(self) -> bool:
        results_files = list(self.results_path.iterdir())
        if not results_files:
            return False
        for counter, file in enumerate(results_files, start=1):
            file.unlink()
        logger.debug(
            f"Deleted {counter} results file(s) at '{self.results_path.resolve()}'")
        return True

    @staticmethod
    def remove_results_dir() -> None:
        try:
            NETUNO_RESULTS_PATH.rmdir()
        except OSError:
            logger.warning(
                "Could not delete the Netuno results directory, probably due to it not "
                "being empty")
        else:
            logger.info(
                f"Successfully deleted Netuno results directory at "
                f"'{NETUNO_RESULTS_PATH.resolve()}'")
