from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "dashboard" / "data" / "processed"


def _date_frame(files: list[Path], station: bool = False) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in files:
        frame = pd.read_csv(path).rename(columns={"DayOFWeek": "DayOfWeek"})
        frame["TravelDate"] = pd.to_datetime(
            frame["TravelDate"].astype(str), format="%Y%m%d", errors="raise"
        )
        if station:
            frame["Station"] = frame["Station"].astype(str).str.strip()
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def _period_columns(columns: list[object]) -> list[str]:
    return [str(column) for column in columns if isinstance(column, str) and "-" in column]


def _read_numbat(path: Path, sheet: str, header_row: int = 2) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet, header=header_row)


def _write_csv(frame: pd.DataFrame, name: str) -> None:
    frame.to_csv(OUTPUT_DIR / f"{name}.csv.gz", index=False, compression="gzip")


def _write_partitioned(frame: pd.DataFrame, name: str, columns: str | list[str]) -> None:
    group_columns = [columns] if isinstance(columns, str) else columns
    for values, partition in frame.groupby(group_columns, observed=True):
        values = values if isinstance(values, tuple) else (values,)
        slug = "_".join(map(str, values)).lower().replace("–", "-").replace("—", "-").replace(" ", "_").replace("/", "_").replace("&", "and")
        _write_csv(partition, f"{name}_{slug}")


def build(source_dir: Path) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    journey_files = sorted(source_dir.glob("Journeys*.csv"))
    station_files = sorted(source_dir.glob("*ootfall*.csv"))
    if len(journey_files) != 7 or len(station_files) != 7:
        raise ValueError("Expected seven journey files and seven station-footfall files")

    journeys = _date_frame(journey_files).rename(
        columns={"TubeJourneyCount": "tube_journeys", "BusJourneyCount": "bus_journeys"}
    )
    journeys["date"] = journeys["TravelDate"]
    journeys["month"] = journeys["date"].dt.to_period("M").dt.to_timestamp()
    journeys["year"] = journeys["date"].dt.year
    journeys["day_of_week"] = journeys["DayOfWeek"]
    journeys["day_type"] = journeys["date"].dt.dayofweek.map(
        lambda value: "Weekday" if value < 5 else "Weekend"
    )
    _write_csv(
        journeys[["date", "month", "year", "day_of_week", "day_type", "tube_journeys", "bus_journeys"]],
        "network_daily",
    )

    footfall = _date_frame(station_files, station=True).rename(
        columns={"Station": "station", "EntryTapCount": "entries", "ExitTapCount": "exits"}
    )
    footfall["month"] = footfall["TravelDate"].dt.to_period("M").dt.to_timestamp()
    footfall["year"] = footfall["TravelDate"].dt.year
    footfall["day_of_week"] = footfall["DayOfWeek"]
    footfall["day_type"] = footfall["TravelDate"].dt.dayofweek.map(
        lambda value: "Weekday" if value < 5 else "Weekend"
    )
    station_period = (
        footfall.groupby(
            ["month", "year", "day_type", "day_of_week", "station"], observed=True, as_index=False
        )
        .agg(entries=("entries", "sum"), exits=("exits", "sum"), active_dates=("TravelDate", "nunique"))
    )
    _write_partitioned(station_period, "station_period", "year")

    kilometres = pd.read_csv(source_dir / "kilometres-operated.csv")
    kilometres = kilometres.loc[:, ~kilometres.columns.str.startswith("Unnamed")]
    kilometres = kilometres.rename(
        columns={
            "Financial Year": "financial_year",
            "Period": "period",
            "Line": "line",
            "Actual KMs in Peak": "actual_peak_km",
            "Scheduled KMs in Peak": "scheduled_peak_km",
            "Actual KMs in Off Peak": "actual_off_peak_km",
            "Scheduled KMs in Off Peak": "scheduled_off_peak_km",
            "Actual KMs Total": "actual_total_km",
            "Scheduled KMs Total": "scheduled_total_km",
        }
    )
    kilometre_fields = [column for column in kilometres if column.endswith("_km")]
    for column in kilometre_fields:
        kilometres[column] = pd.to_numeric(
            kilometres[column].astype(str).str.replace(",", "", regex=False), errors="coerce"
        )
    kilometres["coverage_status"] = "Complete"
    kilometres.loc[
        (kilometres["financial_year"] == "2024-25") & (kilometres["period"].isin([6, 8])),
        "coverage_status",
    ] = "Partial — TfL cyber incident"
    kilometres.loc[
        (kilometres["financial_year"] == "2024-25") & (kilometres["period"] == 7),
        "coverage_status",
    ] = "Unavailable — TfL cyber incident"
    _write_csv(kilometres, "service_records")

    numbat_path = source_dir / "NBT24TWT_outputs.xlsx"
    line_names = _read_numbat(numbat_path, "Line_Boarders")[["Line Code", "Line Name"]].dropna()
    line_name_map = dict(zip(line_names["Line Code"], line_names["Line Name"], strict=False))
    station_parts = []
    for sheet, flow_type in [("Station_Entries", "Entries"), ("Station_Exits", "Exits")]:
        frame = _read_numbat(numbat_path, sheet)
        frame = frame.rename(columns={"Station": "station", "Fare Zone": "fare_zone"})
        frame["flow_type"] = flow_type
        station_parts.append(frame)
    numbat_station = pd.concat(station_parts, ignore_index=True)
    numbat_station = numbat_station.loc[:, ~numbat_station.columns.astype(str).str.startswith("Unnamed")]
    _write_partitioned(numbat_station, "numbat_station", "flow_type")

    platform_parts = []
    for sheet, flow_type in [("Station_Boarders", "Boarders"), ("Station_Alighters", "Alighters")]:
        frame = _read_numbat(numbat_path, sheet)
        frame = frame.rename(
            columns={"Station": "station", "Line": "line", "Dir": "direction", "Mode": "mode"}
        )
        frame["flow_type"] = flow_type
        platform_parts.append(frame)
    numbat_platform = pd.concat(platform_parts, ignore_index=True)
    numbat_platform["line"] = numbat_platform["line"].map(line_name_map).fillna(numbat_platform["line"])
    numbat_platform = numbat_platform.loc[:, ~numbat_platform.columns.astype(str).str.startswith("Unnamed")]
    _write_partitioned(numbat_platform, "numbat_platform", ["flow_type", "line"])

    loads = _read_numbat(numbat_path, "Link_Loads").rename(
        columns={"Line": "line", "Dir": "direction", "From Station": "from_station", "To Station": "to_station"}
    )
    frequencies = _read_numbat(numbat_path, "Link_Frequencies").rename(
        columns={"Line": "line", "Dir": "direction", "From Station": "from_station", "To Station": "to_station"}
    )
    load_qh = _period_columns(list(loads.columns))
    frequency_qh = _period_columns(list(frequencies.columns))
    loads["line"] = loads["line"].map(line_name_map).fillna(loads["line"])
    frequencies["line"] = frequencies["line"].map(line_name_map).fillna(frequencies["line"])
    link_line_map = frequencies.drop_duplicates("Link").set_index("Link")["line"]
    loads["line"] = loads["Link"].map(link_line_map).fillna(loads["line"])
    columns = [
        "Link", "line", "direction", "from_station", "to_station",
        "Total", "Early", "AM Peak", "Midday", "PM Peak", "Evening", "Late",
    ]
    loads = loads[[column for column in columns + load_qh if column in loads.columns]].rename(columns={"Link": "link"})
    frequencies = frequencies[[column for column in columns + frequency_qh if column in frequencies.columns]].rename(columns={"Link": "link"})
    loads["metric_type"] = "Passenger load"
    frequencies["metric_type"] = "Scheduled trains"
    numbat_links = pd.concat([loads, frequencies], ignore_index=True)
    _write_partitioned(numbat_links, "numbat_links", ["metric_type", "line"])

    metadata = {
        "journey_data_from": journeys["date"].min().date().isoformat(),
        "journey_data_through": journeys["date"].max().date().isoformat(),
        "station_data_from": footfall["TravelDate"].min().date().isoformat(),
        "station_data_through": footfall["TravelDate"].max().date().isoformat(),
        "service_financial_years": sorted(kilometres["financial_year"].dropna().unique().tolist()),
        "numbat_context": "NUMBAT 2024 TWT typical autumn Tuesday/Wednesday/Thursday profile",
        "source_files": [path.name for path in journey_files + station_files]
        + ["kilometres-operated.csv", "kilometres-operated-guidance-notes.pdf", "NBT24TWT_outputs.xlsx", "PTSP Oasis for NUMBAT definitions.xlsx"],
        "known_limitations": [
            "Journey and station-footfall sources have different latest dates.",
            "Kilometres operated 2024-25 periods 6 and 8 are partial; period 7 is unavailable after the TfL cyber incident.",
            "NUMBAT is a typical-day model, not an annual observed total.",
            "Passengers per scheduled train is demand intensity, not crowding or capacity utilisation.",
        ],
    }
    (OUTPUT_DIR / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build compact dashboard datasets from the TfL source pack")
    parser.add_argument("source_dir", type=Path, help="Directory containing the uploaded TfL files")
    args = parser.parse_args()
    build(args.source_dir.resolve())
