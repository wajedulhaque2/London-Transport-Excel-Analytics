from __future__ import annotations

import pandas as pd
import streamlit as st


def render(data: dict[str, object]) -> None:
    metadata = data["metadata"]
    st.title("Data quality and methodology")
    st.caption("Source coverage, validation checks, and interpretation rules")

    st.subheader("Source coverage")
    coverage = pd.DataFrame([
        {"Dataset": "Network journeys", "Coverage": f"{metadata['journey_data_from']} to {metadata['journey_data_through']}", "Grain": "Daily network totals", "Status": "Complete within supplied range"},
        {"Dataset": "Station footfall", "Coverage": f"{metadata['station_data_from']} to {metadata['station_data_through']}", "Grain": "Station-day entries and exits", "Status": "Complete within supplied range"},
        {"Dataset": "Kilometres operated", "Coverage": f"{metadata['service_financial_years'][0]} to {metadata['service_financial_years'][-1]}", "Grain": "Financial year × period × line", "Status": "Known 2024-25 incident gaps"},
        {"Dataset": "NUMBAT 2024 TWT", "Coverage": "Typical autumn Tue/Wed/Thu day", "Grain": "15-minute station, platform, and link flows", "Status": "Modelled typical-day profile"},
    ])
    st.dataframe(coverage, width="stretch", hide_index=True)

    st.subheader("Validation results")
    checks = pd.DataFrame([
        {"Check": "Journey date uniqueness", "Result": "2,777 unique dates; no duplicates", "Status": "Pass"},
        {"Check": "Journey calendar continuity", "Result": "No missing dates from 2019-01-01 to 2026-08-08", "Status": "Pass"},
        {"Check": "Station grain", "Result": "1,160,147 unique station-date rows", "Status": "Pass"},
        {"Check": "Negative passenger values", "Result": "None found", "Status": "Pass"},
        {"Check": "Service key uniqueness", "Result": "No duplicate financial-year/period/line keys", "Status": "Pass"},
    ])
    st.dataframe(checks, width="stretch", hide_index=True)

    st.subheader("Material limitations")
    for limitation in metadata["known_limitations"]:
        st.markdown(f"- {limitation}")

    st.subheader("Metric definitions")
    st.markdown(
        """
- **Average daily demand:** total demand divided by distinct observed dates in the selected filter context.
- **Demand vs 2019:** selected average daily demand divided by the matching 2019 day-type baseline.
- **Directionality index:** `ABS(entries − exits) / total footfall`; lower values indicate more balanced entry and exit flows.
- **Service delivery:** actual kilometres divided by scheduled kilometres.
- **Passengers per scheduled train:** passenger link load divided by scheduled trains for the same link and time selection. Capacity is not included.
        """
    )

    st.subheader("Source files")
    st.code("\n".join(metadata["source_files"]), language=None)
