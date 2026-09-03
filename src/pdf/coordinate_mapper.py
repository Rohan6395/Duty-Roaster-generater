from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rect:
    x0: float
    y0: float
    x1: float
    y1: float


class CoordinateMapper:
    """Coordinate helper for template-aware rendering."""

    @staticmethod
    def cell_inner_rect(rect: Rect, padding: float = 1.5) -> Rect:
        return Rect(
            x0=rect.x0 + padding,
            y0=rect.y0 + padding,
            x1=rect.x1 - padding,
            y1=rect.y1 - padding,
        )
