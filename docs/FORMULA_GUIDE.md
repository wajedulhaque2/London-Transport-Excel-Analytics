# Formula, DAX & Power Query Guide

This guide documents the most important logic used in the London Transport Demand & Station Performance workbook.

## 1. Excel formulas

### Workbook navigation

```excel
=HYPERLINK("#'Executive Dashboard'!A1","Executive Dashboard")
```

The same pattern is used for the other workbook-guide links.

### Dashboard KPI retrieval

The dashboard cards use `GETPIVOTDATA` against Data Model PivotTables on `Pivot Support`.

```excel
=GETPIVOTDATA("[Measures].[Average Daily Tube Journeys]",'Pivot Support'!$H$53)
```

```excel
=GETPIVOTDATA("[Measures].[Service Delivery %]",'Pivot Support'!$H$53)
```

```excel
=GETPIVOTDATA("[Measures].[Average Daily Footfall]",'Pivot Support'!$A$1)
```

This keeps the visible dashboard cells linked to the same slicer/filter context as the supporting PivotTables.

### Data-quality status formulas

```excel
=IF(B5>0,"PASS","WARN")
```

```excel
=IF(ISNUMBER(B6),"INFO","WARN")
```

```excel
=IF(B10=0,"PASS","WARN")
```

```excel
=IF(B12>0,"WARN","PASS")
```

The last pattern is deliberately reversed because non-standard performance rows are a known source limitation rather than an unexpected model failure.

---

# 2. Core DAX measures

## Journey demand

### Total Tube Journeys

```DAX
Total Tube Journeys :=
SUM(qJourneys[TubeJourneyCount])
```

### Total Bus Journeys

```DAX
Total Bus Journeys :=
SUM(qJourneys[BusJourneyCount])
```

### Active Journey Days

```DAX
Active Journey Days :=
DISTINCTCOUNT(qJourneys[TravelDate])
```

### Average Daily Tube Journeys

```DAX
Average Daily Tube Journeys :=
DIVIDE(
    [Total Tube Journeys],
    [Active Journey Days]
)
```

### Average Daily Bus Journeys

```DAX
Average Daily Bus Journeys :=
DIVIDE(
    [Total Bus Journeys],
    [Active Journey Days]
)
```

### 2019 Tube baseline

```DAX
2019 Average Daily Tube Journeys :=
CALCULATE(
    [Average Daily Tube Journeys],
    ALL(DimDate[Year]),
    DimDate[Year] = 2019
)
```

### Tube demand vs 2019

```DAX
Tube Demand vs 2019 % :=
DIVIDE(
    [Average Daily Tube Journeys],
    [2019 Average Daily Tube Journeys]
)
```

The Bus baseline and Bus-vs-2019 measure use the same pattern.

---

## Station footfall

The final connected fact table in this build is `qFootfallmerge 1`; earlier `qFootfall` / `qFootfallmerge` queries are staging/intermediate layers.

### Total Entries

```DAX
Total Entries :=
SUM('qFootfallmerge 1'[EntryTapCount])
```

### Total Exits

```DAX
Total Exits :=
SUM('qFootfallmerge 1'[ExitTapCount])
```

### Total Footfall

```DAX
Total Footfall :=
SUM('qFootfallmerge 1'[TotalFootfall])
```

### Active Footfall Days

```DAX
Active Footfall Days :=
DISTINCTCOUNT('qFootfallmerge 1'[TravelDate])
```

### Average Daily Footfall

```DAX
Average Daily Footfall :=
DIVIDE(
    [Total Footfall],
    [Active Footfall Days]
)
```

### Average Daily Entries / Exits

```DAX
Average Daily Entries :=
DIVIDE([Total Entries],[Active Footfall Days])
```

```DAX
Average Daily Exits :=
DIVIDE([Total Exits],[Active Footfall Days])
```

### Directionality Index

```DAX
Directionality Index :=
DIVIDE(
    ABS([Total Entries] - [Total Exits]),
    [Total Footfall]
)
```

Interpretation: values nearer zero have balanced entries/exits; larger values indicate more directional station flows. This is a project-defined analytical measure, not an official TfL metric.

### Weekday / weekend measures

```DAX
Weekday Average Footfall :=
CALCULATE(
    [Average Daily Footfall],
    DimDate[DayType] = "Weekday"
)
```

```DAX
Weekend Average Footfall :=
CALCULATE(
    [Average Daily Footfall],
    DimDate[DayType] = "Weekend"
)
```

```DAX
Weekday Weekend Ratio :=
DIVIDE(
    [Weekday Average Footfall],
    [Weekend Average Footfall]
)
```

### Dynamic station rank

```DAX
Station Rank :=
RANKX(
    ALL(DimFootfallStation[Station]),
    [Average Daily Footfall],
    ,
    DESC,
    DENSE
)
```

### Station demand vs 2019

```DAX
2019 Average Daily Footfall :=
CALCULATE(
    [Average Daily Footfall],
    ALL(DimDate[Year]),
    DimDate[Year] = 2019
)
```

```DAX
Demand vs 2019 % :=
DIVIDE(
    [Average Daily Footfall],
    [2019 Average Daily Footfall]
)
```

---

## Underground performance

### Actual / scheduled kilometres

```DAX
Actual KM :=
SUM(qPerformance[Actual KMs Total])
```

```DAX
Scheduled KM :=
SUM(qPerformance[Scheduled KMs Total])
```

### Service Delivery %

```DAX
Service Delivery % :=
DIVIDE(
    [Actual KM],
    [Scheduled KM]
)
```

### Undelivered KM

```DAX
Undelivered KM :=
[Scheduled KM] - [Actual KM]
```

### Peak delivery

```DAX
Actual Peak KM :=
SUM(qPerformance[Actual KMs in Peak])
```

```DAX
Scheduled Peak KM :=
SUM(qPerformance[Scheduled KMs in Peak])
```

```DAX
Peak Delivery % :=
DIVIDE(
    [Actual Peak KM],
    [Scheduled Peak KM]
)
```

### Off-peak delivery

```DAX
Actual Off-Peak KM :=
SUM(qPerformance[Actual KMs in Off Peak])
```

```DAX
Scheduled Off-Peak KM :=
SUM(qPerformance[Scheduled KMs in Off Peak])
```

```DAX
Off-Peak Delivery % :=
DIVIDE(
    [Actual Off-Peak KM],
    [Scheduled Off-Peak KM]
)
```

### Standard-period service delivery

```DAX
Standard Actual KM :=
CALCULATE(
    [Actual KM],
    qPerformance[PeriodStatus] = "Standard"
)
```

```DAX
Standard Scheduled KM :=
CALCULATE(
    [Scheduled KM],
    qPerformance[PeriodStatus] = "Standard"
)
```

```DAX
Standard Service Delivery % :=
DIVIDE(
    [Standard Actual KM],
    [Standard Scheduled KM]
)
```

### Line rank

```DAX
Line Service Rank :=
RANKX(
    ALL(DimLine[LineName]),
    [Service Delivery %],
    ,
    DESC,
    DENSE
)
```

---

# 3. NUMBAT DAX

## Gate entries / exits

```DAX
NUMBAT Entries :=
SUM(FactNUMBATGate[Entries])
```

```DAX
NUMBAT Exits :=
SUM(FactNUMBATGate[Exits])
```

```DAX
NUMBAT Gate Footfall :=
SUM(FactNUMBATGate[GateFootfall])
```

### Peak-period footfall

```DAX
AM Peak Gate Footfall :=
CALCULATE(
    [NUMBAT Gate Footfall],
    DimQuarterHour[TimeBand] = "AM Peak"
)
```

```DAX
PM Peak Gate Footfall :=
CALCULATE(
    [NUMBAT Gate Footfall],
    DimQuarterHour[TimeBand] = "PM Peak"
)
```

```DAX
Peak Gate Footfall :=
[AM Peak Gate Footfall] + [PM Peak Gate Footfall]
```

```DAX
Peak Share % :=
DIVIDE(
    [Peak Gate Footfall],
    [NUMBAT Gate Footfall]
)
```

## Platform movements

```DAX
NUMBAT Platform Passengers :=
SUM(FactNUMBATPlatform[Passengers])
```

```DAX
NUMBAT Boarders :=
CALCULATE(
    [NUMBAT Platform Passengers],
    FactNUMBATPlatform[MovementType] = "Boarder"
)
```

```DAX
NUMBAT Alighters :=
CALCULATE(
    [NUMBAT Platform Passengers],
    FactNUMBATPlatform[MovementType] = "Alighter"
)
```

```DAX
NUMBAT Platform Flow :=
[NUMBAT Boarders] + [NUMBAT Alighters]
```

```DAX
Net Boarding Flow :=
[NUMBAT Boarders] - [NUMBAT Alighters]
```

## Link load and scheduled frequency

```DAX
Passenger Load :=
SUM(qNUMBATLinkLoads[PassengerLoad])
```

```DAX
Scheduled Trains :=
SUM(qNUMBATLinkFrequencies[ScheduledTrains])
```

```DAX
Passengers per Scheduled Train :=
DIVIDE(
    [Passenger Load],
    [Scheduled Trains]
)
```

Important: this is a demand-intensity measure. It is **not** capacity utilisation because train capacity is not included in the model.

---

# 4. Data-quality DAX

```DAX
Journey Rows :=
COUNTROWS(qJourneys)
```

```DAX
Footfall Rows :=
COUNTROWS('qFootfallmerge 1')
```

```DAX
Distinct Footfall Stations :=
DISTINCTCOUNT(DimFootfallStation[Station])
```

```DAX
Blank Station Rows :=
COUNTROWS(
    FILTER(
        'qFootfallmerge 1',
        ISBLANK('qFootfallmerge 1'[Station])
            || TRIM('qFootfallmerge 1'[Station]) = ""
    )
)
```

```DAX
Negative Footfall Rows :=
COUNTROWS(
    FILTER(
        'qFootfallmerge 1',
        'qFootfallmerge 1'[EntryTapCount] < 0
            || 'qFootfallmerge 1'[ExitTapCount] < 0
    )
)
```

```DAX
Non-Standard Performance Rows :=
COUNTROWS(
    FILTER(
        qPerformance,
        qPerformance[PeriodStatus] <> "Standard"
    )
)
```

---

# 5. Important Power Query patterns

## Folder-combine yearly Journey files

```powerquery
Source = Folder.Files("...\\01_Raw_Data\\Journeys"),
KeepCSV = Table.SelectRows(Source, each [Extension] = ".csv")
```

Each file is parsed and headers are standardised before append.

## Standardise `DayOFWeek` / `DayOfWeek`

```powerquery
StandardiseDayColumn =
    Table.TransformColumnNames(
        CleanColumnNames,
        each if Text.Lower(_) = "dayofweek" then "DayOfWeek" else _
    )
```

## Convert `YYYYMMDD` to a proper date

```powerquery
DateText = Text.PadStart(Text.From(_), 8, "0"),
#date(
    Number.FromText(Text.Start(DateText, 4)),
    Number.FromText(Text.Middle(DateText, 4, 2)),
    Number.FromText(Text.End(DateText, 2))
)
```

## Trim station names

```powerquery
Text.Trim(Text.From([Station]))
```

This resolves source issues such as trailing whitespace while preserving the raw source name separately for auditability.

## Controlled station alias logic

After merging to `qStationAlias`:

```powerquery
if [CanonicalStation] = null
then [Station]
else [CanonicalStation]
```

Examples include:

```text
Canary Wharf EL -> Canary Wharf Elizabeth Line
Custom House EL -> Custom House Elizabeth Line
Woolwich EL -> Woolwich Elizabeth Line
```

The model does not strip mode suffixes globally because `Canary Wharf`, `Canary Wharf DLR` and `Canary Wharf Elizabeth Line` are distinct source entities.

## Performance numeric cleaning

```powerquery
try Number.FromText(
    Text.Replace(
        Text.Trim(Text.From(_)),
        ",",
        ""
    )
)
otherwise null
```

Special values such as `-` therefore become `null`, not zero.

## Performance quality flags

```powerquery
if [Financial Year] = "2024-25" and [PeriodNumber] = 6 then
    "Partial - Cyber Incident"
else if [Financial Year] = "2024-25" and [PeriodNumber] = 8 then
    "Partial - Cyber Incident"
else if [Financial Year] = "2019-20" and [PeriodNumber] = 13 then
    "Special Service"
else if [Financial Year] = "2020-21" and ([PeriodNumber] = 1 or [PeriodNumber] = 2) then
    "Special Service"
else
    "Standard"
```

## NUMBAT unpivot

NUMBAT output files contain 96 quarter-hour columns. The analytical structure is created with:

```powerquery
Table.UnpivotOtherColumns(
    Source,
    {"NLC", "ASC", "Station", "Fare Zone"},
    "QuarterHour",
    "Entries"
)
```

The same pattern is used for Exits, Boarders, Alighters, Link Loads and Link Frequencies.

## Quarter-hour start time

```powerquery
#time(
    Number.FromText(Text.Start([QuarterHour], 2)),
    Number.FromText(Text.Middle([QuarterHour], 2, 2)),
    0
)
```

## NUMBAT time bands

```powerquery
if [StartTime] >= #time(5,0,0) and [StartTime] < #time(7,0,0) then "Early"
else if [StartTime] >= #time(7,0,0) and [StartTime] < #time(10,0,0) then "AM Peak"
else if [StartTime] >= #time(10,0,0) and [StartTime] < #time(16,0,0) then "Midday"
else if [StartTime] >= #time(16,0,0) and [StartTime] < #time(19,0,0) then "PM Peak"
else if [StartTime] >= #time(19,0,0) and [StartTime] < #time(22,0,0) then "Evening"
else "Late"
```

## NUMBAT traffic-day sort

Because the NUMBAT day runs from 05:00 through 04:45 the following morning:

```powerquery
if Time.Hour([StartTime]) < 5
then (Time.Hour([StartTime]) + 24) * 60 + Time.Minute([StartTime])
else Time.Hour([StartTime]) * 60 + Time.Minute([StartTime])
```

This produces a stable 05:00 -> 04:45 sort order for PivotTables and charts.

---

# 6. Model design principles

1. **Dimensions filter facts.** Date, station, line, quarter-hour and link dimensions sit on the `1` side of relationships.
2. **Fact tables are not joined directly to each other.** This prevents ambiguous filters and accidental double counting.
3. **Station Footfall and NUMBAT use separate station dimensions.** Text labels are not forced into one universal station key where the source definitions are ambiguous.
4. **Line demand and line performance remain separate concepts.** Station footfall is not allocated to lines because interchange stations would be double counted.
5. **Source anomalies are flagged, not hidden.** Partial or special-service periods remain visible in Data Quality / Methodology.
