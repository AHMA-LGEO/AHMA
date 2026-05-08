# Indigenous-led Housing Needs Assessment Tool (IHNAT) Dashboard

## Introduction

The Indigenous-led Housing Needs Assessment Tool (IHNAT), developed in collaboration with HART researchers and Statistics Canada, is designed to support Indigenous communities across British Columbia in assessing local housing needs.

The tool is powered by custom census data built by Statistics Canada in collaboration with HART researchers, and covers all census subdivisions (CSDs) in British Columbia, including reserves.

The dashboard allows users to select a census geography comprising any census subdivision (CSD), census division (CD), or the province of British Columbia as a whole, and explore a range of housing, population, income, and shelter indicators for Indigenous and non-Indigenous households.

The dashboard was created in collaboration with Licker Geospatial, who can be reached for further questions regarding dashboard functionality and design.

## Features

The IHNAT dashboard provides the following features:

- Indigenous territory and Métis community identification by geography
- Population and age demographic tables and charts (2006–2021)
- Population breakdowns by Indigenous identity, gender, and ancestry
- Priority population tracking across census years
- Household tenure tables for Indigenous households by community
- Household size comparisons (Indigenous vs. non-Indigenous)
- Income and shelter cost category tables (HART model, 2021)
- Median household and per-person income data (2016, 2021)
- Median shelter costs for owned and rented dwellings
- CMHC rental market survey data (rental units, average rent, vacancy rate)
- Core housing need indicators (affordability, adequacy, suitability) by household type
- Indigenous affordable housing deficit by income and household size
- Systemic pathway data (corrections releases, youth aging out of care)
- Export to Excel for all tables

## Getting Started In Your Local Environment

### System Requirements

Please make sure you have the following installed (a `requirements.txt` is provided in the repository):

- Python 3.10+
- Dash 2.17+
- Pandas
- Plotly
- GeoPandas
- SQLAlchemy
- PostgreSQL (for the data backend)

Install all dependencies with:

```bash
pip install -r requirements.txt
```

### Start Local Server and Run the Dashboard

1. Git clone or download the code package from the repository.
2. Ensure the database connection is configured and `throughputs/` data is in place.
3. Run the application from the project root:

```bash
python app.py
```

4. Open your browser and navigate to:

```
http://localhost:8050/page2
```

> If the localhost address is not recognized, try `http://000.000.0.00:8050/page2` where `000.000.0.00` is your machine's IP address.

### Running the Data Pipeline

To regenerate all dashboard data from source files, run:

```bash
python dataprep/DBUploader.py
```

This will process all source data and write the output tables in database used by the dashboard.

## Technical Support

Please contact [Licker Geospatial](https://lgeo.co) for questions regarding dashboard functionality and design.
