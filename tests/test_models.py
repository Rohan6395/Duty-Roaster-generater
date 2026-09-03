import pytest
from pydantic import ValidationError

from src.models.roster import RosterData, StaffRoster, normalize_duty_code


def test_duty_normalization_spacing() -> None:
    assert normalize_duty_code(" D / O ") == "D/O"
    assert normalize_duty_code(" n / o") == "N/O"


def test_staff_roster_parsing() -> None:
    staff = StaffRoster(
        serial_number=1,
        name="  Alice   Thomas ",
        post=" RN ",
        duties={"1": "m", "2": " D / O "},
    )
    assert staff.name == "Alice Thomas"
    assert staff.post == "RN"
    assert staff.duties[1] == "M"
    assert staff.duties[2] == "D/O"


def test_roster_data_day_validation() -> None:
    with pytest.raises(ValidationError):
        RosterData(
            hospital_name="General",
            roster_title="Duty",
            month=9,
            year=2026,
            total_days=30,
            staff=[
                StaffRoster(
                    serial_number=1,
                    name="A",
                    post="RN",
                    duties={31: "M"},
                )
            ],
        )


def test_invalid_duty_structure_type() -> None:
    with pytest.raises(TypeError):
        StaffRoster(serial_number=1, name="A", post="RN", duties=["M", "E"])
