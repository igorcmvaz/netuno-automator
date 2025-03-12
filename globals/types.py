from dataclasses import dataclass


@dataclass
class Variable:
    label: str
    unit: str
    value: float


@dataclass
class SimulationResults:
    city: str
    model: str
    scenario: str
    potential_savings: Variable
    average_rainwater_consumption: Variable
    average_drinking_water_consumption: Variable
    average_rainwater_overflow: Variable
    period_when_demand_is_fully_met: Variable
    period_when_demand_is_partially_met: Variable
    period_when_demand_is_not_met: Variable
