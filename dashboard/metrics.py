from __future__ import annotations

import math

import pandas as pd


def annual_network_kpis(annual: pd.DataFrame, year: int) -> dict[str, float]:
    selected = annual.loc[annual["year"] == year]
    baseline = annual.loc[annual["year"] == 2019]
    if selected.empty or baseline.empty:
        raise ValueError(f"Missing annual network data for {year} or the 2019 baseline")

    row = selected.iloc[0]
    base = baseline.iloc[0]
    return {
        "tube_avg_daily": float(row["tube_avg_daily"]),
        "bus_avg_daily": float(row["bus_avg_daily"]),
        "tube_vs_2019": safe_divide(row["tube_avg_daily"], base["tube_avg_daily"]),
        "bus_vs_2019": safe_divide(row["bus_avg_daily"], base["bus_avg_daily"]),
    }


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator is None or pd.isna(denominator) or float(denominator) == 0:
        return math.nan
    return float(numerator) / float(denominator)


def compact_number(value: float) -> str:
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}m"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}k"
    return f"{value:,.0f}"


def percent(value: float, decimals: int = 1) -> str:
    if value is None or pd.isna(value):
        return "Not available"
    return f"{float(value):.{decimals}%}"


def ranked_station(top_stations: pd.DataFrame, station: str) -> dict[str, float | int | str]:
    ranked = top_stations.sort_values("average_daily_footfall", ascending=False).reset_index(drop=True)
    row = ranked.loc[ranked["station"] == station]
    if row.empty:
        raise ValueError(f"Station not present in cached ranking: {station}")
    index = int(row.index[0])
    return {
        "station": station,
        "average_daily_footfall": float(row.iloc[0]["average_daily_footfall"]),
        "rank": index + 1,
    }
