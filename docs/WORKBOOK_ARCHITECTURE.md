# Workbook Architecture

## Logical layers

```text
TfL source files
    |
    v
Power Query staging / cleaning
    |
    +--> qJourneys
    +--> qFootfall / qFootfallmerge / qFootfallmerge 1
    +--> qPerformance
    +--> FactNUMBATGate
    +--> FactNUMBATPlatform
    +--> qNUMBATLinkLoads
    +--> qNUMBATLinkFrequencies
    |
    v
Power Pivot Data Model
    |
    +--> DimDate
    +--> DimFootfallStation
    +--> DimLine
    +--> DimNUMBATStation
    +--> DimNUMBATLine
    +--> DimNUMBATLink
    +--> DimQuarterHour
    |
    v
DAX measures
    |
    v
Pivot Support
    |
    v
Dashboards + QA + documentation
```

## Why raw data is not loaded to worksheets

The Station Footfall model contains more than one million rows. Loading the entire source history to ordinary worksheets would hit Excel's worksheet row limit and make the file slower and harder to audit. The project therefore keeps source data external and loads cleaned fact tables to the Data Model / connection-only queries.

That is the intended equivalent of separate `Raw Data` and `Power Query Output` layers in a production workbook.

## User-facing sheets

| Sheet | Role |
|---|---|
| README | Start here / navigation |
| Executive Dashboard | headline KPIs and cross-model summary |
| Network Trends | Tube and Bus demand trends |
| Station Explorer | station-level footfall, ranking and directionality |
| Line Performance | actual vs scheduled Underground service |
| Peak Flow Analysis | NUMBAT station/platform/link demand |
| Data Quality | automated validation checks |
| Methodology | definitions and interpretation rules |
| Source Register | source coverage and transformation notes |

## Supporting sheets

| Sheet | Role |
|---|---|
| Pivot Support | calculation/output layer feeding dashboard cells and charts |
| Lookups | controlled station alias/reference mappings |

## Main relationships

```text
DimDate[Date] 1 -> * qJourneys[TravelDate]
DimDate[Date] 1 -> * qFootfallmerge 1[TravelDate]
DimFootfallStation[Station] 1 -> * qFootfallmerge 1[Station]
DimLine[LineName] 1 -> * qPerformance[LineName]
DimNUMBATStation[NLC] 1 -> * FactNUMBATGate[NLC]
DimNUMBATStation[NLC] 1 -> * FactNUMBATPlatform[NLC]
DimQuarterHour[QuarterHour] 1 -> * NUMBAT fact tables[QuarterHour]
DimNUMBATLink[Link] 1 -> * qNUMBATLinkLoads[Link]
DimNUMBATLink[Link] 1 -> * qNUMBATLinkFrequencies[Link]
```

## Refresh flow

```text
Download/update TfL source files
        -> Refresh All
        -> Power Query transformations
        -> Data Model refresh
        -> DAX measures recalculate
        -> PivotTables/PivotCharts update
```

The portfolio copy is intentionally distributed with cached data so it can be reviewed without recreating the author's local source-folder structure.
