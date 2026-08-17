# Data Sources

## SRC001 - Network Journeys

- **Provider:** Transport for London
- **Workbook coverage:** 01 Jan 2019 - 08 Aug 2026
- **Files:** `Journeys_2019.csv` through `Journeys_2025_2026.csv`
- **Purpose:** daily Tube and Bus demand trends
- **Official page:** https://tfl.gov.uk/corporate/publications-and-reports/network-demand-data
- **Transformation notes:** yearly files are folder-combined in Power Query; `DayOFWeek` is standardised to `DayOfWeek`; `TravelDate` is converted from `YYYYMMDD` to a true date.

## SRC002 - Station Footfall

- **Provider:** Transport for London
- **Workbook coverage:** 01 Jan 2019 - 04 Jul 2026
- **Purpose:** station entry/exit demand, rankings, weekday profiles and station explorer
- **Official page:** https://tfl.gov.uk/corporate/publications-and-reports/network-demand-data
- **Transformation notes:** station names are trimmed, controlled aliases are applied, and missing station-day rows are not manufactured.

## SRC003 - Kilometres Operated

- **Provider:** Transport for London
- **Workbook coverage:** 2016/17 - 2026/27 YTD
- **Purpose:** actual vs scheduled Underground service by line and reporting period
- **Official page:** https://tfl.gov.uk/corporate/publications-and-reports/underground-services-performance
- **Transformation notes:** kilometre text fields are cleaned to numeric; `C&H` is mapped to `Hammersmith & City / Circle` for display; 2024/25 P6 and P8 are flagged as partial and P7 is unavailable.

## SRC004 - NUMBAT 2024 TWT

- **Provider:** Transport for London
- **Coverage:** typical 2024 Tuesday/Wednesday/Thursday profile
- **Workbook:** `NBT24TWT_outputs.xlsx`
- **Purpose:** 15-minute station entries/exits, boarders/alighters, inter-station link loads and scheduled train frequency
- **Official open-data page:** https://tfl.gov.uk/info-for/open-data-users/our-open-data
- **File store:** https://crowding.data.tfl.gov.uk/
- **Transformation notes:** 96 quarter-hour columns are unpivoted into long fact tables. The analytical day is ordered 05:00 through 04:45 the next morning.

## Attribution

Data provided by Transport for London. This repository contains the analytical workbook and documentation; the original TfL source pack is not duplicated in the repository.
