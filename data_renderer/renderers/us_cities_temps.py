from __future__ import annotations

import csv
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from data_renderer.dataset import Dataset


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "datasets"
    / "us_cities_temps"
    / "Highest temperature on record through 2015 by US City.csv"
)
MONTHS = (
    ("JAN", "January"),
    ("FEB", "February"),
    ("MAR", "March"),
    ("APR", "April"),
    ("MAY", "May"),
    ("JUN", "June"),
    ("JUL", "July"),
    ("AUG", "August"),
    ("SEP", "September"),
    ("OCT", "October"),
    ("NOV", "November"),
    ("DEC", "December"),
)
TEMPERATURE_COLOR = "#dc2626"


def _read_temperatures() -> dict[str, list[int | None]]:
    temperatures: dict[str, list[int | None]] = {}
    with DATA_FILE.open(encoding="utf-8-sig", newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            city = row["CITY"]
            if city == "CITY":
                continue
            temperatures[city] = [
                int(row[month]) if row[month] else None for month, _ in MONTHS
            ]
    return temperatures


CITY_TEMPERATURES = _read_temperatures()
CITIES = sorted(CITY_TEMPERATURES, key=str.casefold)


def _city_label(city: str) -> str:
    if "," not in city:
        return city.title()
    name, state = city.rsplit(",", 1)
    return f"{name.title()}, {state.upper()}"


def _load(filters: Mapping[str, str]) -> dict[str, Any]:
    city = filters.get("city", CITIES[0])
    if city not in CITY_TEMPERATURES:
        raise ValueError(f"Unknown city: {city}")

    values = CITY_TEMPERATURES[city]
    observed_values = [value for value in values if value is not None]
    return {
        "id": "us_cities_temps",
        "name": "U.S. City Record Temperatures",
        "description": (
            "Monthly record-high temperatures by U.S. city through 2015."
        ),
        "filters": [
            {
                "id": "city",
                "label": "City",
                "value": city,
                "options": [
                    {"value": option, "label": _city_label(option)}
                    for option in CITIES
                ],
            }
        ],
        "chart": {
            "title": f"Monthly record highs — {_city_label(city)}",
            "xAxis": {"label": "Month"},
            "yAxis": {
                "label": "Temperature (°F)",
                "min": min(observed_values) // 10 * 10,
                "max": (max(observed_values) + 9) // 10 * 10,
            },
            "labels": [label for _, label in MONTHS],
            "series": [
                {
                    "name": "Record high",
                    "color": TEMPERATURE_COLOR,
                    "values": values,
                }
            ],
        },
    }


us_cities_temps_dataset = Dataset(
    id="us_cities_temps",
    name="U.S. City Record Temperatures",
    description="Monthly record-high temperatures by U.S. city through 2015.",
    loader=_load,
)
