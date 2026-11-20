from __future__ import annotations

import unittest

from app import create_app


class DashboardApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = create_app().test_client()

    def test_dataset_list_includes_presidential_elections(self) -> None:
        response = self.client.get("/api/datasets")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]["id"], "us_presidential_elections")

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

    def test_unknown_dataset_is_not_found(self) -> None:
        response = self.client.get("/api/datasets/not_registered")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
