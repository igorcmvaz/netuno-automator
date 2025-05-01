import logging
import subprocess
import time
from pathlib import Path

from globals.constants import NETUNO_STARTUP_WAIT_TIME

logger = logging.getLogger("triton")


class ProcessManager:

    wait_after_start: float
    current_process: subprocess.Popen

    def __init__(self, wait_after_start: float = NETUNO_STARTUP_WAIT_TIME) -> None:
        """
        Initializes the ProcessManager class.

        Args:
            wait_after_start (float, optional): Time, in seconds, to wait after initializing
                Netuno before returning. Defaults to
                `globals.constants.NETUNO_STARTUP_WAIT_TIME`.
        """
        self.wait_after_start = wait_after_start
        self.current_process = None

    def run_netuno(self, path_to_netuno: Path) -> subprocess.Popen:
        """
        Executes the Netuno application in a new process, returning the corresponding Popen
        object.

        Args:
            path_to_netuno (Path): Path to the Netuno executable file.

        Returns:
            subprocess.Popen: New Popen instance corresponding to the process executing
            Netuno.
        """
        self.current_process = subprocess.Popen(args=(path_to_netuno,))
        logger.debug(
            f"Successfully spawned new process #{self.current_process.pid} with Netuno 4")
        time.sleep(self.wait_after_start)
        return self.current_process

    def restart_netuno(self) -> None:
        """
        Restarts the Netuno process, terminating the current one and starting a new one
        with the same executable.
        """
        logger.info(f"Terminating Netuno process #{self.current_process.pid}")
        self.current_process.terminate()
        self.current_process = self.run_netuno(self.current_process.args[0])
