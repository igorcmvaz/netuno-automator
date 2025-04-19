from dataclasses import dataclass

type ResultTuple = tuple[str, str, str, str, str, float, str]


@dataclass
class Variable:
    label: str
    unit: str
    value: float
