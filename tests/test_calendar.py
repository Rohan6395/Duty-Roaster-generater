from src.validation.calendar_validator import (
    build_month_weekdays,
    correct_weekday_labels,
    days_in_month,
    is_leap_year,
    weekday_for_day,
)


def test_leap_year_detection() -> None:
    assert is_leap_year(2024) is True
    assert is_leap_year(2023) is False


def test_days_in_month_variants() -> None:
    assert days_in_month(2023, 2) == 28
    assert days_in_month(2024, 2) == 29
    assert days_in_month(2026, 4) == 30
    assert days_in_month(2026, 5) == 31


def test_weekday_computation() -> None:
    assert weekday_for_day(2026, 9, 1) == "Tue"


def test_correct_weekday_labels_prefers_calendar() -> None:
    corrected, mismatches = correct_weekday_labels(
        2026,
        9,
        {
            1: "Mon",
            2: "Wed",
            3: "Thu",
        },
    )
    assert corrected[1] == "Tue"
    assert 1 in mismatches


def test_build_month_weekdays_length() -> None:
    weekdays = build_month_weekdays(2026, 9)
    assert len(weekdays) == 30
    assert weekdays[30] == "Wed"
