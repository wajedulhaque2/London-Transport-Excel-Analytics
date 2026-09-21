from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dashboard"))

from data_loader import load_snapshot  # noqa: E402
from metrics import (  # noqa: E402
    columns_for_time_band,
    network_summary,
    safe_divide,
    service_summary,
    station_ranking,
)


class MetricsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = load_snapshot()

    def test_source_coverage_and_grain(self) -> None:
        network = self.data["network_daily"]
        station = self.data["station_period"]
        self.assertEqual(len(network), 2777)
        self.assertEqual(network["date"].nunique(), 2777)
        self.assertEqual(network["date"].min(), pd.Timestamp("2019-01-01"))
        self.assertEqual(network["date"].max(), pd.Timestamp("2026-08-08"))
        self.assertEqual(station["year"].min(), 2019)
        self.assertEqual(station["year"].max(), 2026)

    def test_2019_is_the_recovery_baseline(self) -> None:
        kpis = network_summary(self.data["network_daily"], 2019, "All days")
        self.assertAlmostEqual(kpis["tube_vs_2019"], 1.0)
        self.assertAlmostEqual(kpis["bus_vs_2019"], 1.0)

    def test_2025_recovery_matches_documented_values(self) -> None:
        kpis = network_summary(self.data["network_daily"], 2025, "All days")
        self.assertAlmostEqual(kpis["tube_vs_2019"], 0.8482, places=3)
        self.assertAlmostEqual(kpis["bus_vs_2019"], 0.8556, places=3)

    def test_station_ranking_is_fully_available(self) -> None:
        ranking = station_ranking(self.data["station_period"], 2026, "All days")
        self.assertGreater(len(ranking), 400)
        self.assertEqual(ranking.iloc[0]["station"], "Kings Cross St Pancras")
        self.assertGreater(ranking.iloc[0]["average_daily_footfall"], 170_000)

    def test_service_totals_and_rates_are_valid(self) -> None:
        service = self.data["service_records"]
        selected = service.loc[service["financial_year"] == "2025-26"]
        result = service_summary(selected)
        self.assertGreater(result["actual_total_km"], 0)
        self.assertGreater(result["scheduled_total_km"], result["actual_total_km"])
        self.assertGreater(result["service_delivery"], 0.8)
        self.assertLessEqual(result["service_delivery"], 1.0)
        self.assertFalse(service.duplicated(["financial_year", "period", "line"]).any())

    def test_numbat_time_bands_cover_expected_intervals(self) -> None:
        frame = self.data["numbat_station"]
        self.assertEqual(len(columns_for_time_band(frame, "Evening (19:00–22:00)")), 12)
        self.assertEqual(len(columns_for_time_band(frame, "All day")), 96)

    def test_safe_divide_preserves_missing_denominator(self) -> None:
        self.assertTrue(pd.isna(safe_divide(10, 0)))


if __name__ == "__main__":
    unittest.main()
