"""Small platform-neutral placed-token representation (no actor execution)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    identity: str
    name: str
    texture: str
    center: tuple[float, float]  # unpadded background grid coordinates, right/down
    footprint: tuple[float, float]
    texture_scale: tuple[float, float]
    rotation: float  # clockwise degrees
    hidden: bool
    retained_only: tuple[str, ...]
