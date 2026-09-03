from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


def normalize_duty_code(value: str | None) -> str:
    """Normalize whitespace and slash formatting in duty codes."""

    if value is None:
        return ""
    cleaned = str(value).strip()
    if not cleaned:
        return ""
    cleaned = re.sub(r"\s*/\s*", "/", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.upper()


class UncertainCell(BaseModel):
    staff_name: str = Field(min_length=1)
    day: int = Field(ge=1, le=31)
    detected_value: str = Field(default="")
    reason: str = Field(min_length=1)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class StaffRoster(BaseModel):
    serial_number: int = Field(ge=1)
    name: str = Field(min_length=1)
    post: str = Field(default="")
    duties: dict[int, str] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def _clean_name(cls, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

    @field_validator("post")
    @classmethod
    def _clean_post(cls, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

    @field_validator("duties", mode="before")
    @classmethod
    def _normalize_duty_map(cls, duties: Any) -> dict[int, str]:
        if duties is None:
            return {}
        if not isinstance(duties, dict):
            raise TypeError("duties must be an object mapping day to duty code")

        normalized: dict[int, str] = {}
        for raw_day, raw_code in duties.items():
            try:
                day = int(raw_day)
            except Exception as exc:
                raise ValueError(f"invalid day key: {raw_day}") from exc
            if day < 1 or day > 31:
                raise ValueError(f"day out of range: {day}")
            normalized[day] = normalize_duty_code(None if raw_code is None else str(raw_code))
        return normalized


class RosterData(BaseModel):
    hospital_name: str = Field(default="")
    roster_title: str = Field(default="")
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=1900, le=2100)
    total_days: int = Field(ge=28, le=31)
    staff: list[StaffRoster] = Field(default_factory=list)
    uncertain_cells: list[UncertainCell] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_duty_days(self) -> "RosterData":
        for person in self.staff:
            for day in person.duties:
                if day > self.total_days:
                    raise ValueError(
                        f"staff '{person.name}' has duty for day {day}, exceeds total_days={self.total_days}"
                    )
        return self
