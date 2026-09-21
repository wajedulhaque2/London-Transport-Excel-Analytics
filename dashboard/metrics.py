from __future__ import annotations

import math

import pandas as pd


DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
TIME_BANDS = {
    "All day": ("0500-0515", "0445-0500"),
    "Early (05:00–07:00)": ("0500-0515", "0645-0700"),
    "AM peak (07:00–10:00)": ("0700-0715", "0945-1000"),
    "Midday (10:00–16:00)": ("1000-1015", "1545-1600"),
    "PM peak (16:00–19:00)": ("1600-1615", "1845-1900"),
    "Evening (19:00–22:00)": ("1900-1915", "2145-2200"),
    "Late (22:00–05:00)": ("2200-2215", "0445-0500"),
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


def filter_day_type(frame: pd.DataFrame, day_type: str) -> pd.DataFrame:
    return frame if day_type == "All days" else frame.loc[frame["day_type"] == day_type]


def network_summary(frame: pd.DataFrame, year: int, day_type: str) -> dict[str, float]:
    selected = filter_day_type(frame.loc[frame["year"] == year], day_type)
    baseline = filter_day_type(frame.loc[frame["year"] == 2019], day_type)
    if selected.empty or baseline.empty:
        raise ValueError(f"Missing network data for {year}, {day_type}")
    tube = selected["tube_journeys"].mean()
    bus = selected["bus_journeys"].mean()
    return {
        "tube_avg_daily": float(tube), "bus_avg_daily": float(bus),
        "tube_vs_2019": safe_divide(tube, baseline["tube_journeys"].mean()),
        "bus_vs_2019": safe_divide(bus, baseline["bus_journeys"].mean()),
        "active_dates": int(selected["date"].nunique()),
    }


def network_monthly(frame: pd.DataFrame, year: int, day_type: str) -> pd.DataFrame:
    selected = filter_day_type(frame.loc[frame["year"] == year], day_type)
    return selected.groupby("month", as_index=False).agg(
        tube_avg_daily=("tube_journeys", "mean"), bus_avg_daily=("bus_journeys", "mean"), active_dates=("date", "nunique")
    )


def network_weekday(frame: pd.DataFrame, year: int) -> pd.DataFrame:
    selected = frame.loc[frame["year"] == year]
    result = selected.groupby("day_of_week", as_index=False).agg(
        tube_avg_daily=("tube_journeys", "mean"), bus_avg_daily=("bus_journeys", "mean")
    )
    result["day_of_week"] = pd.Categorical(result["day_of_week"], DAY_ORDER, ordered=True)
    return result.sort_values("day_of_week")


def annual_network(frame: pd.DataFrame, day_type: str = "All days") -> pd.DataFrame:
    selected = filter_day_type(frame, day_type)
    return selected.groupby("year", as_index=False).agg(
        tube_avg_daily=("tube_journeys", "mean"), bus_avg_daily=("bus_journeys", "mean"), active_dates=("date", "nunique")
    )


def station_ranking(frame: pd.DataFrame, year: int, day_type: str) -> pd.DataFrame:
    selected = filter_day_type(frame.loc[frame["year"] == year], day_type)
    result = selected.groupby("station", as_index=False).agg(
        entries=("entries", "sum"), exits=("exits", "sum"), active_dates=("active_dates", "sum")
    )
    result["footfall"] = result["entries"] + result["exits"]
    result["average_daily_footfall"] = result["footfall"] / result["active_dates"]
    result["average_daily_entries"] = result["entries"] / result["active_dates"]
    result["average_daily_exits"] = result["exits"] / result["active_dates"]
    result["directionality_index"] = (result["entries"] - result["exits"]).abs() / result["footfall"]
    return result.sort_values("average_daily_footfall", ascending=False).reset_index(drop=True)


def station_monthly(frame: pd.DataFrame, station: str, year: int, day_type: str) -> pd.DataFrame:
    selected = filter_day_type(frame.loc[(frame["station"] == station) & (frame["year"] == year)], day_type)
    result = selected.groupby("month", as_index=False).agg(
        entries=("entries", "sum"), exits=("exits", "sum"), active_dates=("active_dates", "sum")
    )
    result["average_daily_entries"] = result["entries"] / result["active_dates"]
    result["average_daily_exits"] = result["exits"] / result["active_dates"]
    result["average_daily_footfall"] = (result["entries"] + result["exits"]) / result["active_dates"]
    return result


def station_weekday(frame: pd.DataFrame, station: str, year: int) -> pd.DataFrame:
    selected = frame.loc[(frame["station"] == station) & (frame["year"] == year)]
    result = selected.groupby("day_of_week", as_index=False).agg(
        entries=("entries", "sum"), exits=("exits", "sum"), active_dates=("active_dates", "sum")
    )
    result["average_daily_footfall"] = (result["entries"] + result["exits"]) / result["active_dates"]
    result["day_of_week"] = pd.Categorical(result["day_of_week"], DAY_ORDER, ordered=True)
    return result.sort_values("day_of_week")


def service_summary(frame: pd.DataFrame) -> dict[str, float]:
    actual = frame["actual_total_km"].sum(min_count=1)
    scheduled = frame["scheduled_total_km"].sum(min_count=1)
    return {
        "actual_total_km": float(actual), "scheduled_total_km": float(scheduled),
        "service_delivery": safe_divide(actual, scheduled),
        "peak_delivery": safe_divide(frame["actual_peak_km"].sum(min_count=1), frame["scheduled_peak_km"].sum(min_count=1)),
        "off_peak_delivery": safe_divide(frame["actual_off_peak_km"].sum(min_count=1), frame["scheduled_off_peak_km"].sum(min_count=1)),
    }


def quarter_hour_columns(frame: pd.DataFrame) -> list[str]:
    return [column for column in frame.columns if isinstance(column, str) and len(column) == 9 and column[4] == "-"]


def columns_for_time_band(frame: pd.DataFrame, time_band: str) -> list[str]:
    columns = quarter_hour_columns(frame)
    start, end = TIME_BANDS[time_band]
    start_index, end_index = columns.index(start), columns.index(end)
    return columns[start_index : end_index + 1] if start_index <= end_index else columns[start_index:] + columns[: end_index + 1]


def numbat_profile(frame: pd.DataFrame, time_band: str, group_column: str = "flow_type") -> pd.DataFrame:
    columns = columns_for_time_band(frame, time_band)
    grouped = frame.groupby(group_column, observed=True)[columns].sum(min_count=1)
    return grouped.T.rename_axis("quarter_hour").reset_index()
