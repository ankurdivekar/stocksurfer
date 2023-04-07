# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_scrapers.ipynb.

# %% auto 0
__all__ = ['base_path', 'get_request_headers', 'save_daily_bhavcopy', 'fetch_bhavcopy_data_for_range', 'scrape_nse_holidays',
           'get_holidays_table', 'scrape_symbol_list', 'scrape_asm_list', 'scrape_gsm_list', 'scrape_illiquid_list',
           'get_blocklist', 'get_insider_trading_list']

# %% ../nbs/00_scrapers.ipynb 2
import pandas as pd
from datetime import datetime
import requests
import json
from pathlib import Path
import nbdev
import random
import zipfile
import time
import io
from typing import List

# %% ../nbs/00_scrapers.ipynb 3
base_path = nbdev.config.get_config().lib_path

# %% ../nbs/00_scrapers.ipynb 5
def get_request_headers()-> dict:
    user_agents_list = [
        "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
    ]

    return {
        "User-Agent": random.choice(user_agents_list),
        "accept-language": "en,gu;q=0.9,hi;q=0.8",
        "accept-encoding": "gzip, deflate, br",
    }

# %% ../nbs/00_scrapers.ipynb 7
def save_daily_bhavcopy(d, random_delay=True):
    # Get Year, Month, Day
    year = d.year
    month = d.strftime("%B").upper()[:3]
    day = d.date().strftime("%d")

    nse_url = "https://archives.nseindia.com/content/historical/EQUITIES"
    nse_url_2 = "https://www1.nseindia.com/content/historical/EQUITIES"

    # Fetches bhavcopy data for a given date, unzips and saves to local path

    # Define paths
    file_name = f"cm{str(day):02}{month}{year}bhav.csv.zip"
    file_url = f"{nse_url}/{year}/{month}/{file_name}"
    file_url_2 = f"{nse_url_2}/{year}/{month}/{file_name}"

    zip_path = base_path / f"../Data/Bhavcopy/Zips/{file_name}"
    unzip_dir = base_path / "../Data/Bhavcopy/Raw"

    # If file exists, unzip and save to local path
    if Path(zip_path).is_file():
        print(f"File {file_name} already exists.. unzipping")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(unzip_dir)
    else:
        if random_delay:
            time.sleep(random.randint(1, 10))

        headers = get_request_headers()
        print(f"Downloading:{file_url}")

        with requests.Session() as s:
            r = s.get(file_url, allow_redirects=False, headers=headers)

            if r.status_code != 200:
                print(f"Status: {r.status_code}: {file_url}")
                r = s.get(file_url_2, allow_redirects=False, headers=headers)

            if r.status_code != 200:
                print(f"Status: {r.status_code}: {file_url_2}")
                print(f"~~~~~~~~~~~~> Error downloading file: {file_name}")
                # raise Exception(f"Error downloading file: {file_name}")
            else:
                open(zip_path, "wb").write(r.content)
                with zipfile.ZipFile(io.BytesIO(r.content)) as zip_ref:
                    zip_ref.extractall(unzip_dir)
                    print(f"Processed file: {file_name}")


# %% ../nbs/00_scrapers.ipynb 8
def fetch_bhavcopy_data_for_range(start_date, end_date):
    # Get list of holidays
    holidays = get_holidays_table()

    """Fetches bhavcopy data for a given date range and returns a pandas dataframe"""
    for d in pd.date_range(start_date, end_date):
        # Check if date is a NSE holiday
        q = holidays[holidays.tradingDate.str.contains(d.strftime("%d-%b-%Y"))]
        if q.shape[0] > 0:
            print(f"Skipping {d.date()} as it is a holiday: {q.description.values[0]}")
        # Check if date is a weekend
        elif d.weekday() > 4:
            print(f"Skipping {d.date()} as it is a weekend")
        else:
            save_daily_bhavcopy(d, random_delay=True)

    print("Bhavcopy data download complete")


# %% ../nbs/00_scrapers.ipynb 11
def scrape_nse_holidays(segment: str) -> pd.DataFrame:
    # sourcery skip: extract-method
    holidays_url = "https://www.nseindia.com/api/holiday-master?type=trading"

    # Segments for NSE holidays JSON
    segments = {
        "CM": "Equities",
        "MF": "Mutual Funds",
        "SLBS": "Securities Lending &amp; Borrowing Schemes",
        "FO": "Equity Derivatives",
        "CD": "Currency Derivatives",
        "COM": "Commodity Derivatives",
        "IRD": "Interest Rate Derivatives",
        "CBM": "Corporate Bonds",
        "NDM": "New Debt Segment",
        "NTRP": "Negotiated Trade Reporting Platform",
    }
    segments = {v: k for k, v in segments.items()}

    with requests.Session() as sess:
        headers = get_request_headers()

        r = sess.get("https://www.nseindia.com/", headers=headers, timeout=5)
        cookies = dict(r.cookies)
        r = sess.get(holidays_url, headers=headers, timeout=5, cookies=cookies)

        # Unpack json into a dataframe
        tmp = json.loads(r.text)
        return pd.DataFrame(tmp[segments[segment]])


def get_holidays_table(segment: str = "Equities") -> pd.DataFrame:
    holidays_path = Path(
        base_path, "../Data/Misc", f"Holidays_{datetime.now().year}.csv"
    )
    if not holidays_path.exists():
        # holidays_path.parent.mkdir(parents=True, exist_ok=True)
        scrape_nse_holidays(segment).to_csv(holidays_path, index=False)

    return pd.read_csv(holidays_path)


# %% ../nbs/00_scrapers.ipynb 13
def scrape_symbol_list(file_url: str, file_path: str = None) -> List[str]:
    headers = get_request_headers()
    print(f"Downloading:{file_url}")

    headers = get_request_headers()

    with requests.Session() as s:
        request = s.get("https://www.nseindia.com/", headers=headers, timeout=5)
        cookies = dict(request.cookies)
        r = s.get(file_url, headers=headers, timeout=5, cookies=cookies)

        if r.status_code != 200:
            print(f"Status: {r.status_code}: {file_url}")
            print(f"~~~~~~~~~~~~> Error downloading file from: {file_url}")
            # raise Exception(f"Error downloading file: {file_name}")
        else:
            # Parse json from response to dataframe
            tmp = json.loads(r.text)

            if type(tmp) == dict:
                if "longterm" in tmp.keys() and "shortterm" in tmp.keys():
                    # Handles ASM list
                    df_long = pd.DataFrame.from_dict(tmp["longterm"]["data"])
                    df_short = pd.DataFrame.from_dict(tmp["shortterm"]["data"])
                    df = pd.concat([df_long, df_short], axis=0)
                else:
                    # Handles insider list
                    df = pd.DataFrame.from_dict(tmp["data"])

            # Handles GSM list
            elif type(tmp) == list:
                df = pd.DataFrame.from_dict(tmp)

            if file_path:
                df.to_csv(file_path, index=False)
            return df.symbol.to_list()


# %% ../nbs/00_scrapers.ipynb 15
def scrape_asm_list() -> List[str]:
    asm_url = "https://www.nseindia.com/api/reportASM"
    asm_file_path = Path(base_path, "../Data/Misc", "ASM_List.csv")
    return scrape_symbol_list(asm_url, asm_file_path)


def scrape_gsm_list()-> List[str]:
    gsm_url = "https://www.nseindia.com/api/reportGSM"
    gsm_file_path = Path(base_path, "../Data/Misc", "GSM_List.csv")
    return scrape_symbol_list(gsm_url, gsm_file_path)

# %% ../nbs/00_scrapers.ipynb 17
def scrape_illiquid_list() -> List[str]:
    illiquid_sheet = "https://docs.google.com/spreadsheets/d/1xGjim5zIQbaP1oXm0EEIU28PMxkyFwW2ufyVoB-O-i8/export?gid=251665721&format=csv"
    df = pd.read_csv(illiquid_sheet)
    return df.Symbol.to_list()

# %% ../nbs/00_scrapers.ipynb 19
def get_blocklist() -> List[str]:
    gsm = scrape_gsm_list()
    asm = scrape_asm_list()
    illiquid = scrape_illiquid_list()
    return list(set(asm + gsm + illiquid))

# %% ../nbs/00_scrapers.ipynb 21
def get_insider_trading_list()-> List[str]:
    insider_url = "https://www.nseindia.com/api/corporates-pit?index=equities"
    insider_file_path = Path(base_path, "../Data/Misc", "Insider_List.csv")
    return scrape_symbol_list(insider_url, insider_file_path)
