from __future__ import annotations

import csv
from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from data_renderer.dataset import Dataset


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "datasets"
    / "us_presidential_elections"
    / "1976-2024-president.csv"
)
PARTIES = ("DEMOCRAT", "REPUBLICAN", "LIBERTARIAN", "OTHER")
PARTY_COLORS = {
    "DEMOCRAT": "#2563eb",
    "REPUBLICAN": "#dc2626",
    "LIBERTARIAN": "#d97706",
    "OTHER": "#64748b",
}


def _read_results() -> tuple[
    list[str],
    list[str],
    dict[str, dict[str, dict[str, int]]],
    dict[str, dict[str, int]],
]:
    state_party_votes: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(int))
    )
    state_total_votes: dict[str, dict[str, int]] = defaultdict(dict)

    with DATA_FILE.open(encoding="utf-8-sig", newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            year = row["year"]
            state = row["state"]
            party = row["party_simplified"] or "OTHER"
            state_party_votes[state][year][party] += int(row["candidatevotes"])
            state_total_votes[state][year] = int(row["totalvotes"])

    states = sorted(state_party_votes)
    years = sorted(
        {year for yearly_votes in state_party_votes.values() for year in yearly_votes},
        key=int,
    )
    return years, states, state_party_votes, state_total_votes


YEARS, STATES, STATE_PARTY_VOTES, STATE_TOTAL_VOTES = _read_results()


def _make_chart(location: str) -> dict[str, Any]:
    if location == "UNITED_STATES":
        party_votes: dict[str, dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        total_votes: dict[str, int] = defaultdict(int)
        for state in STATES:
            for year, votes in STATE_PARTY_VOTES[state].items():
                for party, count in votes.items():
                    party_votes[year][party] += count
                total_votes[year] += STATE_TOTAL_VOTES[state][year]
        location_label = "United States"
    else:
        party_votes = STATE_PARTY_VOTES[location]
        total_votes = STATE_TOTAL_VOTES[location]
        location_label = location.title()

    series = []
    for party in PARTIES:
        values = []
        for year in YEARS:
            denominator = total_votes.get(year, 0)
            values.append(
                party_votes.get(year, {}).get(party, 0) / denominator
                if denominator
                else 0
            )
        series.append(
            {"name": party.title(), "color": PARTY_COLORS[party], "values": values}
        )

    return {
        "title": f"Presidential vote share — {location_label}",
        "xAxis": {"label": "Election year"},
        "yAxis": {
            "label": "Share of the vote",
            "min": 0,
            "max": 1,
            "format": "percent",
        },
        "labels": YEARS,
        "series": series,
    }


def _load(filters: Mapping[str, str]) -> dict[str, Any]:
    location = filters.get("location", "UNITED_STATES")
    if location != "UNITED_STATES" and location not in STATE_PARTY_VOTES:
        raise ValueError(f"Unknown location: {location}")

    return {
        "id": "us_presidential_elections",
        "name": "U.S. Presidential Elections",
        "description": "Party vote share by election year and state or nationwide.",
        "filters": [
            {
                "id": "location",
                "label": "Location",
                "value": location,
                "options": [
                    {"value": "UNITED_STATES", "label": "United States (national)"}
                ]
                + [{"value": state, "label": state.title()} for state in STATES],
            }
        ],
        "chart": _make_chart(location),
    }


presidential_elections_dataset = Dataset(
    id="us_presidential_elections",
    name="U.S. Presidential Elections",
    description="Party vote share by election year and state or nationwide.",
    loader=_load,
)
