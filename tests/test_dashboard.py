from __future__ import annotations

import csv
import unittest
from datetime import datetime
from pathlib import Path

from app import create_app


class DashboardApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = create_app().test_client()

    def test_dataset_list_includes_presidential_elections(self) -> None:
        response = self.client.get("/api/datasets")

        self.assertEqual(response.status_code, 200)
        dataset_ids = [dataset["id"] for dataset in response.json]
        self.assertIn("us_presidential_elections", dataset_ids)
        self.assertIn("nba_games", dataset_ids)

    def test_national_chart_has_expected_years_and_party_series(self) -> None:
        response = self.client.get("/api/datasets/us_presidential_elections")

        self.assertEqual(response.status_code, 200)
        payload = response.json
        self.assertEqual(payload["chart"]["labels"], [str(year) for year in range(1976, 2025, 4)])
        self.assertEqual(
            [series["name"] for series in payload["chart"]["series"]],
            ["Democrat", "Republican", "Libertarian", "Other"],
        )
        self.assertEqual(payload["filters"][0]["value"], "UNITED_STATES")
        for year_index in range(len(payload["chart"]["labels"])):
            share_sum = sum(
                series["values"][year_index] for series in payload["chart"]["series"]
            )
            self.assertLess(abs(share_sum - 1.0), 0.001)

    def test_state_filter_returns_state_specific_shares(self) -> None:
        national_response = self.client.get(
            "/api/datasets/us_presidential_elections"
        )
        response = self.client.get(
            "/api/datasets/us_presidential_elections?location=CALIFORNIA"
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json
        self.assertIn("California", payload["chart"]["title"])
        self.assertEqual(payload["filters"][0]["value"], "CALIFORNIA")
        self.assertNotEqual(
            payload["chart"]["series"][0]["values"],
            national_response.json["chart"]["series"][0]["values"],
        )

    def test_invalid_location_is_a_client_error(self) -> None:
        response = self.client.get(
            "/api/datasets/us_presidential_elections?location=NOT_A_STATE"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unknown location", response.json["error"])

    def test_nba_chart_uses_selected_team_and_season_year(self) -> None:
        data_file = (
            Path(__file__).resolve().parents[1]
            / "datasets"
            / "nba_games"
            / "Games.csv"
        )
        with data_file.open(encoding="utf-8-sig", newline="") as csv_file:
            game = next(csv.DictReader(csv_file))

        game_date = datetime.fromisoformat(game["gameDateTimeEst"])
        season_year = str(game_date.year + (game_date.month >= 7))
        response = self.client.get(
            "/api/datasets/nba_games",
            query_string={"team": game["hometeamId"], "year": season_year},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json
        chart = payload["chart"]
        game_index = chart["labels"].index(game_date.strftime("%Y-%m-%d"))
        self.assertEqual(payload["filters"][0]["value"], game["hometeamId"])
        self.assertEqual(payload["filters"][1]["value"], season_year)
        self.assertEqual(chart["series"][0]["values"][game_index], int(game["homeScore"]))
        self.assertIn(game["awayteamName"], chart["series"][0]["pointLabels"][game_index])

    def test_invalid_nba_team_is_a_client_error(self) -> None:
        response = self.client.get(
            "/api/datasets/nba_games?team=NOT_A_TEAM"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unknown NBA team", response.json["error"])

    def test_unknown_dataset_is_not_found(self) -> None:
        response = self.client.get("/api/datasets/not_registered")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
