from src.models.roster import RosterData, StaffRoster
from src.validation.roster_validator import validate_roster_data


def test_duplicate_staff_rows() -> None:
    roster = RosterData(
        hospital_name="Hosp",
        roster_title="Nursing Officer",
        month=9,
        year=2026,
        total_days=30,
        staff=[
            StaffRoster(serial_number=1, name="Asha", post="RN", duties={1: "M"}),
            StaffRoster(serial_number=2, name="asha", post="RN", duties={1: "E"}),
        ],
    )
    errors = validate_roster_data(roster)
    assert any("duplicate staff rows" in e for e in errors)


def test_missing_day_handling_allows_partial() -> None:
    roster = RosterData(
        hospital_name="Hosp",
        roster_title="Nursing Officer",
        month=9,
        year=2026,
        total_days=30,
        staff=[
            StaffRoster(serial_number=1, name="Asha", post="RN", duties={1: "M", 3: "E"}),
        ],
    )
    errors = validate_roster_data(roster)
    assert errors == []


def test_month_year_validation_mismatch_total_days() -> None:
    roster = RosterData(
        hospital_name="Hosp",
        roster_title="Nursing Officer",
        month=2,
        year=2023,
        total_days=29,
        staff=[
            StaffRoster(serial_number=1, name="Asha", post="RN", duties={1: "M"}),
        ],
    )
    errors = validate_roster_data(roster)
    assert any("does not match calendar days" in e for e in errors)


def test_duplicate_serial_number_validation() -> None:
    roster = RosterData(
        hospital_name="Hosp",
        roster_title="Nursing Officer",
        month=9,
        year=2026,
        total_days=30,
        staff=[
            StaffRoster(serial_number=1, name="Asha", post="RN", duties={1: "M"}),
            StaffRoster(serial_number=1, name="Bella", post="RN", duties={1: "E"}),
        ],
    )
    errors = validate_roster_data(roster)
    assert any("duplicate serial numbers" in e for e in errors)
