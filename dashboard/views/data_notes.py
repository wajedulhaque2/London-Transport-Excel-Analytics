from __future__ import annotations

import streamlit as st


def render(data: dict[str, object]) -> None:
    metadata = data["metadata"]
    quality = data["data_quality"].copy()
    sources = data["source_register"].copy()

    st.title("Data quality and methodology")
    st.caption("Source coverage, validation checks and interpretation rules")

    st.subheader("Cached workbook checks")
    st.dataframe(quality, width="stretch", hide_index=True)

    st.subheader("Source register")
    st.dataframe(
        sources[["source_id", "dataset", "coverage", "purpose", "status"]],
        width="stretch",
        hide_index=True,
    )

    st.subheader("Material limitations")
    for limitation in metadata["limitations"]:
        st.markdown(f"- {limitation}")

    st.subheader("Metric definitions")
    st.markdown(
        """
        - **Average daily demand:** total demand divided by distinct active dates in the matching filter context.
        - **Demand vs 2019:** current average daily demand divided by the matching 2019 baseline.
        - **Directionality Index:** `ABS(entries - exits) / total footfall`; lower values are more balanced.
        - **Service Delivery %:** actual kilometres divided by scheduled kilometres.
        - **Passengers per Scheduled Train:** passenger load divided by scheduled trains. Capacity is not included.
        """
    )

    st.subheader("Snapshot lineage")
    st.json(
        {
            "source_workbook": metadata["source_workbook"],
            "portfolio_build_refresh": metadata["portfolio_build_refresh"],
            "snapshot_extracted_at": metadata["snapshot_extracted_at"],
            "journey_data_through": metadata["journey_data_through"],
            "station_data_through": metadata["station_data_through"],
        },
        expanded=False,
    )
