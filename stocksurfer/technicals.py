# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_technicals.ipynb.

# %% auto 0
__all__ = ['base_path', 'get_raw_bhavcopy_data', 'preprocess', 'get_sma', 'get_bollinger_bands', 'get_donchian', 'get_supertrend',
           'add_candle_stats', 'add_all_technicals', 'process_all_symbols']

# %% ../nbs/02_technicals.ipynb 3
import pandas as pd
import os
import numpy as np
from pathlib import Path
import pandas_ta as pdta
import nbdev
import shutil


# %% ../nbs/02_technicals.ipynb 4
base_path = nbdev.config.get_config().lib_path


# %% ../nbs/02_technicals.ipynb 7
def get_raw_bhavcopy_data():
    bhavcopy_dtypes = {
        "SYMBOL": "string",
        "SERIES": "string",
        "OPEN": "float64",
        "HIGH": "float64",
        "LOW": "float64",
        "CLOSE": "float64",
        "TOTTRDQTY": "int64",
        "TOTTRDVAL": "float64",
        "TIMESTAMP": "string",
        "TOTALTRADES": "int64",
        # "ISIN": 'string',
        # "Unnamed: 13": 'string',
    }

    bhavcopy_usecols = [
        "SYMBOL",
        "SERIES",
        "OPEN",
        "HIGH",
        "LOW",
        "CLOSE",
        "TOTTRDQTY",
        "TOTTRDVAL",
        "TIMESTAMP",
        "TOTALTRADES",
    ]

    raw_data_dir = base_path / "../Data/Bhavcopy/Raw"
    csv_files = [x for x in raw_data_dir.iterdir() if x.suffix == ".csv"]

    # TODO remove this, its only for testing
    # csv_files = csv_files[:201]

    # Read all the csv files and concatenate them into one dataframe
    return pd.concat(
        [
            pd.read_csv(
                f,
                dtype=bhavcopy_dtypes,
                usecols=bhavcopy_usecols,
                parse_dates=["TIMESTAMP"],
                dayfirst=False,
            )
            for f in csv_files
        ],
        ignore_index=True,
    )

# %% ../nbs/02_technicals.ipynb 9
def preprocess(df):
    return (
        df.pipe(lambda x: x[x["SERIES"] == "EQ"])
        .assign(
            DATE=pd.to_datetime(df.TIMESTAMP, format="%Y-%M-%d").dt.date,
            DAY_OF_WEEK=pd.to_datetime(df.TIMESTAMP, format="%d-%b-%Y").dt.day_name(),
            WEEK_NUM=pd.to_datetime(df.TIMESTAMP, format="%d-%b-%Y")
            .dt.isocalendar()
            .week,
        )
        .drop(
            columns=[
                "TIMESTAMP",
            ]
        )
        .sort_values(["SYMBOL", "DATE"])
        .reset_index(drop=True)
        # .set_index("DATE")
    )

# %% ../nbs/02_technicals.ipynb 12
# Generate simple moving average data
def get_sma(df_symbol, period=20, metric="CLOSE"):
    if metric.upper() in ["CLOSE", "OPEN", "HIGH", "LOW"]:
        return pd.concat(
            [
                df_symbol,
                pdta.sma(df_symbol[metric], length=period).rename(
                    f"SMA_{period}_{metric.upper()[0]}"
                ),
            ],
            axis=1,
        )
    else:
        raise ValueError("Invalid metric")

# %% ../nbs/02_technicals.ipynb 14
# Generate bollinger bands data
def get_bollinger_bands(df_symbol, period=20, std=2):
    return pd.concat(
        [
            df_symbol,
            pdta.bbands(df_symbol.CLOSE, length=period, std=std).rename(
                columns={
                    f"BBU_{period}_{std:.1f}": f"BBU_{period}_{std}",
                    f"BBM_{period}_{std:.1f}": f"BBM_{period}_{std}",
                    f"BBL_{period}_{std:.1f}": f"BBL_{period}_{std}",
                    f"BBB_{period}_{std:.1f}": f"BBB_{period}_{std}",
                    f"BBP_{period}_{std:.1f}": f"BBP_{period}_{std}",
                }
            ),
        ],
        axis=1,
    )

# %% ../nbs/02_technicals.ipynb 16
# Generate donchian channel data
def get_donchian(df_symbol, upper=22, lower=66):
    return pd.concat(
        [
            df_symbol,
            pdta.donchian(
                df_symbol.HIGH, df_symbol.LOW, lower_length=66, upper_length=22
            )
            # .rename(
            #     columns={
            #         f"DCL_{lower}_{upper}": f"DONCHIAN_L{lower}",
            #         f"DCU_{lower}_{upper}": f"DONCHIAN_U{upper}"})
            .drop(columns=[f"DCM_{lower}_{upper}"]),
        ],
        axis=1,
    )

# %% ../nbs/02_technicals.ipynb 18
# Generate supertrend data
def get_supertrend(df_symbol, period=12, multiplier=3):
    return pd.concat(
        [
            df_symbol,
            pdta.supertrend(
                df_symbol.HIGH,
                df_symbol.LOW,
                df_symbol.CLOSE,
                length=period,
                multiplier=multiplier,
            )
            .drop(
                columns=[
                    f"SUPERT_{period}_{multiplier:.1f}",
                    f"SUPERTl_{period}_{multiplier:.1f}",
                    f"SUPERTs_{period}_{multiplier:.1f}",
                ]
            )
            .rename(
                columns={
                    f"SUPERTd_{period}_{multiplier:.1f}": f"ST_{period}_{multiplier}"
                }
            ),
        ],
        axis=1,
    )

# %% ../nbs/02_technicals.ipynb 20
def add_candle_stats(df_symbol):
    return df_symbol.assign(
        CDL_COLOR=df_symbol.apply(
            lambda x: "green" if x.CLOSE > x.OPEN else "red", axis=1
        ).astype("string"),
        CDL_SIZE=abs(df_symbol.CLOSE - df_symbol.OPEN),
        TOPWICK_SIZE=df_symbol.HIGH - df_symbol[["OPEN", "CLOSE"]].max(axis=1),
        BOTWICK_SIZE=df_symbol[["OPEN", "CLOSE"]].min(axis=1) - df_symbol.LOW,
    )

# %% ../nbs/02_technicals.ipynb 22
# Generate all technicals for a symbol data
def add_all_technicals(df_symbol):
    return (
        df_symbol.sort_values(["SYMBOL", "DATE"])
        .reset_index(drop=True)
        # Add SMA
        .pipe(get_sma, period=20, metric="CLOSE")
        .pipe(get_sma, period=20, metric="HIGH")
        .pipe(get_sma, period=44, metric="CLOSE")
        .pipe(get_sma, period=200, metric="CLOSE")
        # Add Bollinger bands
        .pipe(get_bollinger_bands)
        # Add Donchian channel
        .pipe(get_donchian)
        # Add supertrend data
        .pipe(get_supertrend, period=12, multiplier=3)
        .pipe(get_supertrend, period=11, multiplier=2)
        .pipe(get_supertrend, period=10, multiplier=1)
        # Add candle properties data
        .pipe(add_candle_stats)
    )

# %% ../nbs/02_technicals.ipynb 24
def process_all_symbols():
    df = get_raw_bhavcopy_data()
    df = preprocess(df)

    processed_data_dir = base_path / "../Data/Bhavcopy/Processed"
    
    # Recursively delete all files and directories inside the processed data directory
    _ = [
        shutil.rmtree(f) if f.is_dir() else f.unlink()
        for f in processed_data_dir.iterdir()
    ]

    for symbol, df_symbol in df.groupby("SYMBOL"):
        if len(df_symbol) > 200:
            df_symbol = add_all_technicals(df_symbol)

            file_path = processed_data_dir / f"{symbol}.parquet"
            df_symbol.to_parquet(file_path, index=True)
            print(f"Saved {file_path.name}")
