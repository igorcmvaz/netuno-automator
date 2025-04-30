import logging
import subprocess
import time
from argparse import ArgumentParser
from pathlib import Path
from collections.abc import Callable

from agents.automators import NetunoAutomator
from agents.exporter import CSVExporter
from agents.parsers import FileNameParser, ResultParser
from agents.validators import CommandLineArgsValidator
from globals.constants import (
    INITIAL_DATES, NETUNO_RESULTS_PATH, NETUNO_STARTUP_WAIT_TIME, SIMULATION_PARAMETERS)
from globals.errors import (
    InvalidNetunoExecutableError, InvalidPartialSaveAttributeError,
    InvalidSourceDirectoryError, MissingInputDataError)

logger = logging.getLogger("triton")


def run_netuno(
        path_to_netuno: Path,
        wait_after_start: int = NETUNO_STARTUP_WAIT_TIME) -> subprocess.Popen:
    """
    Executes the Netuno application in a new process, returning the corresponding Popen
    object.

    Args:
        path_to_netuno (Path): Path to the Netuno executable file.
        wait_after_start (int): Time, in seconds, to wait after initializing Netuno before
        returning. Defaults to `globals.constants.NETUNO_STARTUP_WAIT_TIME`.

    Returns:
        subprocess.Popen: New Popen instance corresponding to the process executing Netuno.
    """
    new_process = subprocess.Popen(args=(path_to_netuno,))
    logger.debug(f"Successfully spawned new process #{new_process.pid} with Netuno 4")
    time.sleep(wait_after_start)
    return new_process


def setup_logger(
        logger: logging.Logger, quiet_count: int = 0, verbose: bool = False) -> None:
    """
    Configures a logger for the application, defining output format and log level according
    to quiet or verbose arguments.

    Args:
        logger (logging.Logger): Logger channel to be configured.
        quiet_count (int): Number of times the 'quiet' flag was provided. Defaults to 0.
        verbose (bool): Whether the 'verbose' flag was provided. Defaults to False.
    """
    if verbose:
        log_level = logging.DEBUG
    elif quiet_count == 1:
        log_level = logging.WARNING
    elif quiet_count >= 2:
        log_level = logging.ERROR
    else:
        log_level = logging.INFO

    logger.propagate = True
    logger.setLevel(log_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s  %(levelname)-8.8s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z")
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def sleep_until(function: Callable, tick: float = 0.01) -> None:
    """
    Sleep until a function returns True, checking it at fixed intervals.

    Args:
        function (Callable): Function to evaluate at every interval.
        tick (float, optional): Interval between checks, in seconds. Defaults to 0.01.
    """
    while not function():
        time.sleep(tick)


def main(args: CommandLineArgsValidator):
    global_start_time = time.perf_counter()
    automator = NetunoAutomator()
    exporter = CSVExporter(Path(__file__).parent)
    NETUNO_RESULTS_PATH.mkdir(exist_ok=True)

    dir_generator = args.precipitation_dir_path.iterdir()
    first_file = next(dir_generator)
    city, model, scenario = FileNameParser.get_metadata(first_file)
    logger.info(
        f"Processing first file, containing data from the city of '{city}', "
        f"model '{model}', scenario '{scenario}'")
    results_file = automator.run_first_simulation(
        first_file, INITIAL_DATES[scenario], **SIMULATION_PARAMETERS)

    sleep_until(results_file.is_file)
    exporter.add_results(ResultParser(results_file).to_list(city, model, scenario))
    if args.clean:
        results_file.unlink()
        logger.debug(f"Deleted results file at '{results_file.resolve()}'")

    iteration_start_time = time.perf_counter()
    for counter, input_file in enumerate(dir_generator, start=1):
        city, model, scenario = FileNameParser.get_metadata(input_file)
        logger.info(f"Processing city of '{city}', model '{model}', scenario '{scenario}'")
        results_file = automator.run_simulation(input_file, INITIAL_DATES[scenario])
        sleep_until(results_file.is_file)

        exporter.add_results(ResultParser(results_file).to_list(city, model, scenario))
        if counter % args.save_every == 0:
            logger.info(f"Saving results to disk at iteration #{counter}")
            exporter.save_results()
        if args.clean:
            results_file.unlink()
            logger.debug(f"Deleted results file at '{results_file.resolve()}'")

    exporter.save_results()
    logger.info(f"Successfully saved results at '{exporter.output_path.resolve()}'")

    end_time = time.perf_counter()
    total_iteration_time = end_time - iteration_start_time
    logger.info(
        f"Completed all operations. "
        f"Total time: {end_time - global_start_time:.2f}s. "
        f"Total iteration time: {total_iteration_time:.2f}s. "
        f"Average iteration time ({counter} entries): {total_iteration_time/counter:.2f}s")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "netuno_exe_path", metavar="path/to/netuno.exe", type=Path,
        help="path to a Netuno executable file")
    parser.add_argument(
        "precipitation_dir_path", metavar="path/to/precipitation", type=Path,
        help=(
            "path to a directory containing the input precipitation data files, in CSV "
            "format"))
    parser.add_argument(
        "-q", "--quiet", action="count", default=0,
        help="turn on quiet mode (cumulative), which hides log entries of levels lower "
        "than WARNING, then ERROR. Ignored if --verbose is present")
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help=(
            "turn on verbose mode, to display all log messages of level DEBUG and above. "
            "Overrides --quiet"))
    parser.add_argument(
        "--clean", action="store_true", default=False,
        help="delete result files generated by Netuno at the end")
    parser.add_argument(
        "-n", "--save-every", type=int, default=10, dest="save_every",
        help="number of files to process before saving the in-memory results to a file. "
        "Must be a positive integer. Defaults to 10.")

    validator = CommandLineArgsValidator()
    parser.parse_args(namespace=validator)
    setup_logger(logger, validator.quiet, validator.verbose)

    try:
        validator.validate_arguments()
    except (
            InvalidNetunoExecutableError,
            InvalidSourceDirectoryError,
            InvalidPartialSaveAttributeError,
            MissingInputDataError) as exception:
        logger.exception(f"Command line arguments validation failed. Details:\n{exception}")
        raise SystemExit

    netuno_process = run_netuno(validator.netuno_exe_path)
    try:
        main(validator)
    except Exception as exception:
        logger.exception(f"An error occurred during the operation. Details:\n{exception}")
    finally:
        netuno_process.terminate()
