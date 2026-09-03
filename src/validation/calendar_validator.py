from __future__ import annotations

import calendar
from datetime import date


def is_leap_year(year: int) -> bool:
    return calendar.isleap(year)


def days_in_month(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


def weekday_for_day(year: int, month: int, day: int) -> str:
    return date(year, month, day).strftime("%a")


def build_month_weekdays(year: int, month: int) -> dict[int, str]:
    total = days_in_month(year, month)
    return {day: weekday_for_day(year, month, day) for day in range(1, total + 1)}


def correct_weekday_labels(
    year: int,
    month: int,
    extracted: dict[int, str] | None,
) -> tuple[dict[int, str], list[int]]:
    """Return calendar-based weekdays and list of mismatched day numbers."""

    expected = build_month_weekdays(year, month)
    if not extracted:
        return expected, []

    mismatches: list[int] = []
    for day, expected_label in expected.items():
        label = (extracted.get(day, "") or "").strip().title()
        if label and label != expected_label:
            mismatches.append(day)
    return expected, mismatches
