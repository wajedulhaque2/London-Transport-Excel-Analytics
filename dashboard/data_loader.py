from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent / "data" / "cached"

TABLES = {
    "network_monthly": "network_monthly.csv",
    "network_annual": "network_annual.csv",
    "network_weekday": "network_weekday.csv",
    "top_stations": "top_stations.csv",
    "station_monthly_detail": "station_monthly_detail.csv",
    "station_weekday_detail": "station_weekday_detail.csv",
    "station_entries_exits_detail": "station_entries_exits_detail.csv",
    "service_reporting_period": "service_reporting_period.csv",
    "service_by_line": "service_by_line.csv",
    "service_peak_offpeak_by_line": "service_peak_offpeak_by_line.csv",
    "executive_service_by_line": "executive_service_by_line.csv",
    "numbat_gate_evening": "numbat_gate_evening.csv",
    "numbat_platform_evening": "numbat_platform_evening.csv",
    "numbat_intensity_evening": "numbat_intensity_evening.csv",
    "numbat_link_load_evening": "numbat_link_load_evening.csv",
    "executive_numbat_intensity": "executive_numbat_intensity.csv",
    "source_register": "source_register.csv",
    "data_quality": "data_quality.csv",
}


@lru_cache(maxsize=1)
def load_snapshot() -> dict[str, object]:
    data: dict[str, object] = {
        name: pd.read_csv(DATA_DIR / filename) for name, filename in TABLES.items()
    }
    with (DATA_DIR / "snapshot_meta.json").open(encoding="utf-8") as handle:
        data["metadata"] = json.load(handle)

    monthly = data["network_monthly"]
    annual = data["network_annual"]
    station_monthly = data["station_monthly_detail"]
    station_entries_exits = data["station_entries_exits_detail"]

    monthly["month"] = pd.to_datetime(monthly["month"], format="%Y-%m")
    annual["year"] = annual["year"].astype(int)
    station_monthly["month"] = pd.to_datetime(station_monthly["month"], format="%Y-%m")
    station_entries_exits["month"] = pd.to_datetime(
        station_entries_exits["month"], format="%Y-%m"
    )
    return data
