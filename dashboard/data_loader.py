from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent / "data" / "processed"

TABLES = {
    "network_daily": "network_daily.csv.gz",
    "station_period": "station_period_*.csv.gz",
    "service_records": "service_records.csv.gz",
    "numbat_station": "numbat_station_*.csv.gz",
    "numbat_platform": "numbat_platform_*.csv.gz",
    "numbat_links": "numbat_links_*.csv.gz",
}


@lru_cache(maxsize=1)
def load_snapshot() -> dict[str, object]:
    data: dict[str, object] = {}
    for name, pattern in TABLES.items():
        files = sorted(DATA_DIR.glob(pattern))
        if not files:
            raise FileNotFoundError(f"No processed dashboard files match {pattern}")
        data[name] = pd.concat([pd.read_csv(path) for path in files], ignore_index=True)
    with (DATA_DIR / "metadata.json").open(encoding="utf-8") as handle:
        data["metadata"] = json.load(handle)

    network = data["network_daily"]
    network["date"] = pd.to_datetime(network["date"])
    network["month"] = pd.to_datetime(network["month"])
    data["station_period"]["month"] = pd.to_datetime(data["station_period"]["month"])
    data["service_records"]["period"] = data["service_records"]["period"].astype(int)
    return data
