# Live dashboard

This Streamlit application turns the cached Excel portfolio into a shareable web dashboard while leaving the workbook unchanged.

## Run locally

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard/app.py
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`.

## Data architecture

The application reads small, versioned CSV snapshots in `dashboard/data/cached/`. These were extracted from the workbook's cached Pivot Support outputs, not reconstructed from invented rows.

The original TfL source pack is not stored in this repository. As a result:

- Network monthly and annual comparisons are available through August 2026.
- The detailed Station Explorer view is limited to the workbook's cached Langdon Park / 2026 / Weekday context. Other cached leading stations expose ranking and average daily footfall only.
- Line Performance uses the workbook's cached multi-financial-year selection.
- NUMBAT quarter-hour output is limited to the cached Evening slice.

Unavailable detail is shown explicitly in the app. Missing observations are not converted to zero.

## Rebuild the snapshots

The source workbook remains at `workbook/London_Transport_Demand_Analytics_Portfolio.xlsx`. To rebuild the web snapshots after updating its cached pivots:

```bash
python dashboard/scripts/extract_cached_snapshot.py
```

The extractor opens the workbook read-only and writes CSV/JSON outputs under `dashboard/data/cached/`.

## Deploy with Streamlit Community Cloud

1. Push this branch to GitHub.
2. In Streamlit Community Cloud, create an app from this repository.
3. Choose `dashboard/app.py` as the entrypoint.
4. Deploy. No secrets are required for the cached version.

The later refresh upgrade should replace the cached snapshots with a controlled TfL ingestion pipeline. Keep calendar-year demand filters separate from TfL financial-year service filters.
