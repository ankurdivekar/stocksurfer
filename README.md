stocksurfer
================

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

> Install: Currently not pip installable. Under heavy development. Until
> then, clone the repo and run `pip install -e .` from the root
> directory.

``` sh
pip install stocksurfer
```

## How to use

Get the latest NSE data

``` python
from datetime import datetime

# Define date range
start_date = datetime(2023,4, 15)
end_date = datetime.now()

# Fetch data from NSE
fetch_bhavcopy_data_for_range(start_date, end_date)
```

    --------------------------------------------------
    Fetching data for 15 days
    Skipping 2023-04-15 as it is a weekend
    Skipping 2023-04-16 as it is a weekend
    File cm17APR2023bhav.csv.zip already exists.. unzipping
    File cm18APR2023bhav.csv.zip already exists.. unzipping
    File cm19APR2023bhav.csv.zip already exists.. unzipping
    File cm20APR2023bhav.csv.zip already exists.. unzipping
    File cm21APR2023bhav.csv.zip already exists.. unzipping
    Skipping 2023-04-22 as it is a holiday: Id-Ul-Fitr (Ramzan ID)
    Skipping 2023-04-23 as it is a weekend
    File cm24APR2023bhav.csv.zip already exists.. unzipping
    File cm25APR2023bhav.csv.zip already exists.. unzipping
    File cm26APR2023bhav.csv.zip already exists.. unzipping
    File cm27APR2023bhav.csv.zip already exists.. unzipping
    File cm28APR2023bhav.csv.zip already exists.. unzipping
    Skipping 2023-04-29 as it is a weekend
    Skipping 2023-04-30 as it is a weekend
    Bhavcopy data download complete
    --------------------------------------------------

Generate stock data with technical indicators added

``` python
update_all_symbols_data()
```

    2023-04-27 2023-04-30
    --------------------------------------------------
    Fetching data for 3 days
    File cm27APR2023bhav.csv.zip already exists.. unzipping
    File cm28APR2023bhav.csv.zip already exists.. unzipping
    Skipping 2023-04-29 as it is a weekend
    Skipping 2023-04-30 as it is a weekend
    Bhavcopy data download complete
    --------------------------------------------------
    No new data to update

Get list of stocks in ASM and GSM

``` python
# get_blocklist()
```
