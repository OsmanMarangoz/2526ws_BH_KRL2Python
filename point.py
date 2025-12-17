from dataclasses import dataclass

@dataclass
class Point6D:
    name: str
    x: float
    y: float
    z: float
    a: float
    b: float
    c: float

@dataclass
class JointState:
    a1: float
    a2: float
    a3: float
    a4: float
    a5: float
    a6: float