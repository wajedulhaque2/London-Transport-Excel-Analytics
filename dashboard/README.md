# Live dashboard

This Streamlit application turns the supplied TfL source pack into a shareable, fully interactive web dashboard while leaving the Excel portfolio unchanged.

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

The app reads compact, versioned source-backed datasets in `dashboard/data/processed/`. They were generated from:

- daily Tube and bus journey files covering 2019 through 8 August 2026;
- daily station entries and exits covering 2019 through 4 July 2026;
- Underground kilometres operated by financial year, reporting period, and line;
- complete NUMBAT 2024 TWT station, platform, link-load, and service-frequency outputs.

The processed station table retains station, month, day type, and day-of-week grain. The NUMBAT datasets retain all 96 quarter-hour intervals. This keeps the deployed app responsive without limiting its filters to cached PivotTable selections.

## Rebuild the processed datasets

Place the original TfL files in one folder, then run:

```bash
python dashboard/scripts/build_raw_snapshot.py /path/to/source-folder
```

The command validates the expected source families and rewrites `dashboard/data/processed/`. The source files themselves are not required by the deployed app.

## Interpretation

- Calendar-year passenger demand remains separate from financial-year service performance.
- Journey and station sources show their own latest dates.
- Kilometres-operated periods 6 and 8 of 2024-25 are partial; period 7 is unavailable after the TfL cyber incident.
- NUMBAT represents a typical autumn Tuesday/Wednesday/Thursday profile, not an annual total.
- Passengers per scheduled train is demand intensity, not train occupancy, crowding, or capacity utilisation.

## Deploy with Streamlit Community Cloud

1. Push the updated branch to GitHub and merge its pull request.
2. In Streamlit Community Cloud, create or reboot the app from this repository.
3. Use `dashboard/app.py` as the entrypoint.
4. No secrets are required.
