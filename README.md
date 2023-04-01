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

``` python
from datetime import datetime
```

Get the latest NSE data

``` python
# Define date range
start_date = datetime(2023, 3, 20)
end_date = datetime.now()

# Fetch data from NSE
# fetch_bhavcopy_data_for_range(start_date, end_date)
```

Get list of stocks in ASM and GSM

``` python
# get_blocklist()
```

Generate stock data with technical indicators added

``` python
# process_all_symbols()
```
