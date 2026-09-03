from __future__ import annotations

from collections import Counter

from src.models.roster import RosterData
from src.validation.calendar_validator import days_in_month


def validate_roster_data(roster: RosterData) -> list[str]:
    """Return validation errors list; empty means valid for generation."""

    errors: list[str] = []

    expected_days = days_in_month(roster.year, roster.month)
    if roster.total_days != expected_days:
        errors.append(
            f"total_days={roster.total_days} does not match calendar days {expected_days}"
        )

    staff_names = [person.name.strip().lower() for person in roster.staff if person.name.strip()]
    duplicate_names = [name for name, count in Counter(staff_names).items() if count > 1]
    if duplicate_names:
        errors.append(f"duplicate staff rows: {', '.join(duplicate_names)}")

    serials = [person.serial_number for person in roster.staff]
    duplicate_serials = [str(s) for s, count in Counter(serials).items() if count > 1]
    if duplicate_serials:
        errors.append(f"duplicate serial numbers: {', '.join(duplicate_serials)}")

    for person in roster.staff:
        invalid_days = [str(day) for day in person.duties.keys() if day < 1 or day > roster.total_days]
        if invalid_days:
            errors.append(f"invalid day keys for {person.name}: {', '.join(invalid_days)}")

    return errors
