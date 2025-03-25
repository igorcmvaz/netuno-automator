COEFFICIENT_OF_LOSS_MIN = 0.1
COEFFICIENT_OF_LOSS_MAX = 1.0
RAINFALL_SUBSTITUTION_PERCENT_MIN = 10
RAINFALL_SUBSTITUTION_PERCENT_MAX = 100

NETUNO_STARTUP_WAIT_TIME = 1
PAUSE = 0.8
PATH_TO_LOWER_TANK_RADIO_BUTTON = r"static\netuno_lower_tank_known_volume.png"

INITIAL_DATES = {
    "Histórico": "1980-01-01",
    "SSP245": "2015-01-01",
    "SSP585": "2015-01-01"
}

SIMULATION_PARAMETERS = {
    "initial_run_off_disposal": 2,
    "catchment_area": 50,
    "daily_water_demand": 603,
    "number_of_residents": 1,
    "rainwater_replacement_percentage": 40,
    "coefficient_of_loss": 0.8,
    "inferior_tank_capacity": 150
}

SIMULATION_OUTPUT_ATTRIBUTES = {
    "encoding": "WINDOWS-1252",
    "delimiter": ";",
    "skip_n_rows": 22
}
