# Netuno Automator

This repository holds the code for a tool designed to automate parts of the workflow for "Netuno 4", a software which estimates potential savings in drinking water by utilizing rainwater where potable water is not required. This automation tool simplifies the process of running multiple simulations of different precipitation data files with the same parameters, and compiling the results into a single CSV output file.

For more information about Netuno 4, including download links and manuals, [their project page](https://labeee.ufsc.br/downloads/softwares/netuno).

## Overview

The automator assumes the input precipitation files already have the correct format for Netuno 4, that is: one row with value of precipidation (in mm) for each day in the desired period, no headers. We further assume the files follow a specific naming convention that identifies location, climate model and scenario (see more details at the [`FileNameParser` class](./agents/parsers.py#L13)).

Currently, the supported climate periods are:

* `Histórico`: from 1980-01-01 to 2013-12-31
* `SSP2-4.5`: from 2015-01-01 to 2100-12-31
* `SSP5-8.5`: from 2015-01-01 to 2100-12-31

The simulation setup is performed once, and then all subsequent files are processed using the same parameters (detailed at [`constants.py`](./globals/constants.py#L29)).

The output file is a single CSV file containing the following columns:

* `city`: Name of the city corresponding to the precipitation data (from file name)
* `model`: Name of the climate model (from file name)
* `scenario`: Name of the climate scenario (from file name)
* `metric`: Name of the metric evaluated, used in code (e.g. `average_rainwater_consumption`)
* `label`: Label of the metric given by Netuno 4 (e.g. `Volume consumido médio de água pluvial (litros/dia)`)
* `value`: Value of the metric resulted from the simulation
* `unit`: Unit in which the metric is displayed (e.g. `liters/day`)

## Setup

To set up the project, follow these steps:

1. Clone the repository:

    ```bash
    git clone git@github.com:igorcmvaz/netuno-automator.git
    cd netuno-automator
    ```

2. Create and activate a virtual environment (Python 3.10+ required):

    ```bash
    python -m venv .venv        # Use your preferred Python3.10+ executable here
    .venv/Scripts/activate      # On Windows
    source .venv/bin/activate   # On Linux
    ```

3. Install dependencies:

    ```bash
    python -m pip install -r requirements.txt
    ```

4. Verify the installation:

    ```bash
    python triton.py -h
    ```

## Usage

This is a command-line tool, and can receive many different parameters through the terminal that serve to configure and change how the operation takes place. However, the main functionality is comprised of the following flow:

1. Validate command line arguments
2. Start a new process running the Netuno 4 executable
3. Setup the simulation parameters in Netuno 4
4. Execute for each precipitation file:
    1. Run simulation with given precipitation file
    2. Parse results from the simulation
    3. (When applicable) Save to disk the results obtained so far, delete Netuno result files
    4. (When applicable) Restart the Netuno 4 process and reconfigure the simulation parameters
5. Consolidate all results in a CSV file
6. Delete the results directory created for Netuno 4 output files
7. Terminate the Netuno 4 process

### Recommendations

* Since mouse and keyboard inputs are simulated to operate the Netuno 4 GUI, using the machine for other purposes is not possible, as any interferences with keyboard, mouse and application focus may cause unexpected behavior. In case you need to make an unplanned stop of the process, try to **move the mouse to the top right corner of the screen**, which will trigger `PyAutoGUI`'s fail-safe feature and stop the script.
* Since part of the operation relies on finding the exact position of elements on the screen, use a single monitor when executing it, preferably with scale at 100%, to reduce the chances of running into issues.
* Avoid using the keyboard and mouse during the execution of the script, as it may interfere with the simulation process, and avoid taking actions that might result in notifications, popups or loss of focus.
* Disable screensavers and sleep mode, since for longer operations they may cause the machine to lock and interrupt the process.

### Running the Script

In order to execute such operation, the application requires a source of CSV precipitation data files and a path to the Netuno 4 executable. Here are a couple of examples:

```bash
# show help message and details about the parameters
python triton.py -h
# run with default parameters           
python triton.py path/to/netuno.exe path/to/precipitation

python triton.py path/to/netuno.exe path/to/precipitation -q        # hide INFO logs
python triton.py path/to/netuno.exe path/to/precipitation -qq       # hide INFO and WARNING logs
python triton.py path/to/netuno.exe path/to/precipitation -v        # show DEBUG logs
python triton.py path/to/netuno.exe path/to/precipitation --clean   # delete intermediate Netuno 4 result files
python triton.py path/to/netuno.exe path/to/precipitation -w 2      # add a 0.2 second wait time after opening Windows Explorer
python triton.py path/to/netuno.exe path/to/precipitation -n 5      # save results to disk every 5 files
python triton.py path/to/netuno.exe path/to/precipitation -r 10     # restar the Netuno aplication every 10 files

# hide INFO logs, save results every 100 files, restart Netuno every 15 files, add a 1 second wait after opening Explorer, and delete intermediate result files
python triton.py path/to/netuno.exe path/to/precipitation -qn100 -r15 -w10 --clean
```

The consolidated CSV file containing the simulation results for the processed files is saved in the root directory with a timestamped filename, e.g., `2025-01-12T13-45-consolidated.csv`.

## Troubleshooting

If during the operation you notice `PyAutoGUI` is not able to find the elements on the screen, more specifically the radio button labeled "Simulação para reservatório com volume conhecido", please open Netuno 4 and take a screenshot similar to [netuno_lower_tank_known_volume.png](./static/netuno_lower_tank_known_volume.png) and replace it (keep the same name!) before running the script again. This is the image used by `PyAutoGUI` to find the element on the screen.

## Tests

The project includes a comprehensive test suite using `pytest`. Tests cover all major functionalities, including edge cases and error handling.

### Running Tests

To run the test suite, use the following commands:

```bash
python -m pytest
python -m pytest -v               # Verbose output
python -m pytest -o log_cli=true  # Show logs during tests
python -m pytest --cov            # Run coverage analysis (requires pytest-cov)
```

### Test Dependencies

The following dependencies are required for testing:

* `pytest`
* `pytest-cov` (optional, for coverage analysis)
* `time-machine` (for mocking `now()` from `datetime` module)

### Coverage

To generate a coverage report:

```bash
python -m pytest --cov=agents --cov-report=html
```

The coverage report will be available in the `htmlcov` directory.

## Commits

When committing to this repository, the following convention is advised:

* **chore**: regular maintenance unrelated to source code (dependencies, config, etc)
* **docs**: updates to any documentation
* **feat**: new features
* **fix**: bug fixes
* **ref**: refactored code (no new feature or bug fix)
* **test**: updates to tests

For further reference on writing good commit messages, see [Conventional Commits](https://www.conventionalcommits.org).
