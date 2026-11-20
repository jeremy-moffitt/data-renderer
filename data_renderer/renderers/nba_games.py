from __future__ import annotations

import csv
import math
from collections import defaultdict
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any

from data_renderer.dataset import Dataset


DATA_FILE = Path(__file__).resolve().parents[2] / "datasets" / "nba_games" / "Games.csv"
NBA_BLUE = "#2563eb"


def _read_games() -> tuple[
    list[str],
    dict[str, str],
    dict[str, dict[str, list[tuple[datetime, int, str]]]],
]:
    latest_team_labels: dict[str, tuple[datetime, str]] = {}
    team_games: dict[str, dict[str, list[tuple[datetime, int, str]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    years: set[str] = set()

    with DATA_FILE.open(encoding="utf-8-sig", newline="") as csv_file:
        for row in csv.DictReader(csv_file):
            game_date = datetime.fromisoformat(row["gameDateTimeEst"])
            season_year = str(game_date.year + (game_date.month >= 7))
            years.add(season_year)

            home_team_id = row["hometeamId"]
            away_team_id = row["awayteamId"]
            home_team = f"{row['hometeamCity']} {row['hometeamName']}"
            away_team = f"{row['awayteamCity']} {row['awayteamName']}"

            for team_id, label in (
                (home_team_id, home_team),
                (away_team_id, away_team),
            ):
                previous = latest_team_labels.get(team_id)
                if previous is None or game_date > previous[0]:
                    latest_team_labels[team_id] = (game_date, label)

            team_games[home_team_id][season_year].append(
                (
                    game_date,
                    int(row["homeScore"]),
                    f"{game_date:%Y-%m-%d} vs {away_team}: {row['homeScore']} points",
                )
            )
            team_games[away_team_id][season_year].append(
                (
                    game_date,
                    int(row["awayScore"]),
                    f"{game_date:%Y-%m-%d} at {home_team}: {row['awayScore']} points",
                )
            )

    labels = {
        team_id: label for team_id, (_, label) in latest_team_labels.items()
    }
    return sorted(years, key=int, reverse=True), labels, dict(team_games)


YEARS, TEAM_LABELS, TEAM_GAMES = _read_games()


def _load(filters: Mapping[str, str]) -> dict[str, Any]:
    year = filters.get("year", YEARS[0])
    if year not in YEARS:
        raise ValueError(f"Unknown NBA season year: {year}")

    teams_in_year = sorted(
        (
            team_id
            for team_id, yearly_games in TEAM_GAMES.items()
            if year in yearly_games
        ),
        key=lambda team_id: TEAM_LABELS[team_id].casefold(),
    )
    team_id = filters.get("team", teams_in_year[0])
    if team_id not in TEAM_LABELS:
        raise ValueError(f"Unknown NBA team: {team_id}")
    if year not in TEAM_GAMES.get(team_id, {}):
        raise ValueError(f"{TEAM_LABELS[team_id]} did not play in {year}.")

    games = sorted(TEAM_GAMES[team_id][year], key=lambda game: game[0])
    points = [game[1] for game in games]
    chart_max = max(10, math.ceil(max(points) / 10) * 10)

    years_for_team = sorted(TEAM_GAMES[team_id], key=int, reverse=True)
    return {
        "id": "nba_games",
        "name": "NBA Games",
        "description": (
            "Points scored by a franchise in each game. Years are labeled by "
            "the season-ending year."
        ),
        "filters": [
            {
                "id": "team",
                "label": "Team",
                "value": team_id,
                "options": [
                    {"value": option_id, "label": TEAM_LABELS[option_id]}
                    for option_id in teams_in_year
                ],
            },
            {
                "id": "year",
                "label": "Year",
                "value": year,
                "options": [
                    {"value": option_year, "label": option_year}
                    for option_year in years_for_team
                ],
            },
        ],
        "chart": {
            "title": f"{TEAM_LABELS[team_id]} points per game — {year}",
            "xAxis": {"label": "Game date"},
            "yAxis": {"label": "Points scored", "min": 0, "max": chart_max},
            "labels": [game[0].strftime("%Y-%m-%d") for game in games],
            "series": [
                {
                    "name": "Points",
                    "color": NBA_BLUE,
                    "values": points,
                    "pointLabels": [game[2] for game in games],
                }
            ],
        },
    }


nba_games_dataset = Dataset(
    id="nba_games",
    name="NBA Games",
    description="Points scored by a franchise in each game and season.",
    loader=_load,
)
