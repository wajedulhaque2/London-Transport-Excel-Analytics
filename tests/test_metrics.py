from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dashboard"))

from data_loader import load_snapshot  # noqa: E402
from metrics import annual_network_kpis, ranked_station, safe_divide  # noqa: E402


class MetricsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = load_snapshot()

    def test_2019_is_the_recovery_baseline(self) -> None:
        kpis = annual_network_kpis(self.data["network_annual"], 2019)
        self.assertAlmostEqual(kpis["tube_vs_2019"], 1.0)
        self.assertAlmostEqual(kpis["bus_vs_2019"], 1.0)

    def test_2025_recovery_matches_documented_values(self) -> None:
        kpis = annual_network_kpis(self.data["network_annual"], 2025)
        self.assertAlmostEqual(kpis["tube_vs_2019"], 0.8482, places=3)
        self.assertAlmostEqual(kpis["bus_vs_2019"], 0.8556, places=3)

    def test_safe_divide_preserves_missing_denominator(self) -> None:
        self.assertTrue(pd.isna(safe_divide(10, 0)))

    def test_top_station_rank(self) -> None:
        result = ranked_station(self.data["top_stations"], "Kings Cross St Pancras")
        self.assertEqual(result["rank"], 1)
        self.assertGreater(result["average_daily_footfall"], 170_000)

    def test_cached_months_are_unique(self) -> None:
        months = self.data["network_monthly"]["month"]
        self.assertEqual(months.nunique(), len(months))
        self.assertFalse(months.isna().any())

    def test_missing_station_rows_are_not_created(self) -> None:
        detail = self.data["station_monthly_detail"]
        self.assertEqual(len(detail), 7)
        self.assertFalse((detail["average_daily_footfall"] == 0).any())

    def test_required_snapshots_have_no_missing_measure_values(self) -> None:
        required = [
            "network_monthly",
            "network_annual",
            "network_weekday",
            "top_stations",
            "service_by_line",
            "service_reporting_period",
            "numbat_gate_evening",
            "numbat_platform_evening",
        ]
        for table in required:
            self.assertFalse(self.data[table].isna().any().any(), table)

    def test_rates_and_counts_are_in_valid_ranges(self) -> None:
        self.assertTrue(self.data["service_by_line"]["service_delivery"].between(0, 1).all())
        self.assertTrue(
            self.data["service_peak_offpeak_by_line"][["peak_delivery", "off_peak_delivery"]]
            .apply(lambda column: column.between(0, 1).all())
            .all()
        )
        self.assertTrue(
            (self.data["numbat_gate_evening"][["entries", "exits"]] >= 0).all().all()
        )


if __name__ == "__main__":
    unittest.main()
