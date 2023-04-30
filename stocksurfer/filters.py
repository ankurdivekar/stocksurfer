# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_filters.ipynb.

# %% auto 0
__all__ = ['base_path', 'processed_data_dir', 'nifty500_csv', 'get_nifty500', 'get_symbol_data', 'get_monthly_data',
           'get_weekly_data', 'single_candle_span', 'hammer_on_BBL', 'green_engulfing_on_BBL',
           'three_rising_green_candles_on_SMA20', 'sma20_catch', 'filter_stocks']

# %% ../nbs/04_filters.ipynb 3
import pandas as pd
from datetime import datetime, timedelta
import nbdev
from .technicals import add_all_technicals, get_sma

# %% ../nbs/04_filters.ipynb 4
base_path = nbdev.config.get_config().lib_path

# %% ../nbs/04_filters.ipynb 5
processed_data_dir = base_path / "../Data/Bhavcopy/Processed/"
nifty500_csv = base_path / "../Data/Misc/ind_nifty500list.csv"

# %% ../nbs/04_filters.ipynb 7
def get_nifty500():
    # Get Nifty500 list
    return pd.read_csv(nifty500_csv).Symbol.to_list()

# %% ../nbs/04_filters.ipynb 8
# Load data for a symbol
def get_symbol_data(symbol):
    file_path = base_path / processed_data_dir / f"{symbol}.parquet"

    if not file_path.exists():
        return None
    df = pd.read_parquet(file_path)
    df["DATE"] = pd.to_datetime(df['DATE'])#apply(lambda x: x.strftime('%Y-%d-%m'))
    return df

# %% ../nbs/04_filters.ipynb 9
# Convert daily data to monthly data
def get_monthly_data(df):
    return df.resample('M', on='DATE').agg({'OPEN': 'first', 'HIGH': 'max', 'LOW': 'min', 'CLOSE': 'last','SYMBOL': 'first', 'DATE': 'first'}).reset_index(drop=True)

# Convert daily data to weekly data
def get_weekly_data(df):
    return df.resample('W', on='DATE').agg({'OPEN': 'first', 'HIGH': 'max', 'LOW': 'min', 'CLOSE': 'last','SYMBOL': 'first', 'DATE': 'first'}).reset_index(drop=True)

# %% ../nbs/04_filters.ipynb 10
# Check if the latest candle spans the given SMAs
def single_candle_span(df, kwargs=None):
    if kwargs and 'col_list' in kwargs.keys():
        col_list = kwargs['col_list']
    else:
        col_list = ["SMA_20_C", "SMA_200_C"]
    
    conditions = [
        df.LOW.iloc[-1] <= df[col].iloc[-1] <= df.HIGH.iloc[-1]
        for col in col_list
    ]
    if all(conditions):
        print(
            f"{df.SYMBOL.iloc[0]} -> Single candle span on {df.DATE.iloc[-1]}"
        )
        return True
    return False

# %% ../nbs/04_filters.ipynb 11
# Check if the latest candle is a hammer
def hammer_on_BBL(df, kwargs=None):
    
    body = df.iloc[-1].CLOSE - df.iloc[-1].OPEN
    upper_wick = df.iloc[-1].HIGH - df.iloc[-1].CLOSE
    lower_wick = df.iloc[-1].OPEN - df.iloc[-1].LOW
    
    conditions = [
        df.iloc[-1].CLOSE > df.iloc[-1].OPEN,
        lower_wick >= 2*body,
        body >= 1.5*upper_wick,
        df.iloc[-1].CLOSE > df.iloc[-1].BBL_20_2 > df.iloc[-1].LOW,
    ]
    
    if all(conditions):
        print(f"{df.SYMBOL.iloc[0]} -> Hammer on BBL on {df.DATE.iloc[-1]}")
        return True
    return False

# %% ../nbs/04_filters.ipynb 12
# Check if latest candle is green takes out red on BBL
def green_engulfing_on_BBL(df, kwargs=None):
    conditions = [
        df.iloc[-2].CLOSE < df.iloc[-2].OPEN,
        df.iloc[-1].CLOSE > df.iloc[-1].OPEN,
        df.iloc[-1].LOW < df.iloc[-1].BBL_20_2 < df.iloc[-1].HIGH,
        df.iloc[-1].CLOSE > df.iloc[-2].OPEN,
    ]
    
    if all(conditions):
        print(f"{df.SYMBOL.iloc[0]} -> Green engulfing on BBL on {df.DATE.iloc[-1]}")
        return True
    return False

# %% ../nbs/04_filters.ipynb 13
# Check for three rising green candles
def three_rising_green_candles_on_SMA20(df, kwargs=None):
    conditions = [
        df.iloc[-1].CLOSE > df.iloc[-1].OPEN,
        df.iloc[-2].CLOSE > df.iloc[-2].OPEN,
        df.iloc[-3].CLOSE > df.iloc[-3].OPEN,
    
        df.iloc[-1].CLOSE > df.iloc[-2].CLOSE,
        df.iloc[-2].CLOSE > df.iloc[-3].CLOSE,
        
        df.iloc[-3].CLOSE > df.iloc[-3].SMA_20_C,
        df.iloc[-3].LOW < df.iloc[-3].SMA_20_C,
    ]
    
    if all(conditions):
        print(f"{df.SYMBOL.iloc[0]} -> Three rising green candles on {df.DATE.iloc[-1]}")
        return True
    return False

# %% ../nbs/04_filters.ipynb 14
# Check for SMA 20 catch
def sma20_catch(df, kwargs=None):
    conditions = [
        df.iloc[-1].CLOSE > df.iloc[-1].OPEN,
        df.iloc[-2].CLOSE > df.iloc[-2].OPEN,
        
        df.iloc[-2].LOW < df.iloc[-2].SMA_20_C,
        df.iloc[-1].LOW > df.iloc[-1].SMA_20_C,
    ]
    
    if all(conditions):
        print(f"{df.SYMBOL.iloc[0]} -> SMA 20 catch on {df.DATE.iloc[-1]}")
        return True

# %% ../nbs/04_filters.ipynb 15
def filter_stocks(symbols=None, timeframe = "daily", cutoff_date = None, strategy=None, strategy_args=None, ):
    
    if not symbols:
        symbols = get_nifty500()
    elif symbols == "all":
        symbols = [f.stem for f in processed_data_dir.glob("*.parquet")] 
    for symbol in symbols:
        df = get_symbol_data(symbol)
        if df is None:
            print(f"Data not found for {symbol}")
        else:
            if cutoff_date:
                df = df.query("DATE < @cutoff_date")
            if timeframe.lower() == "monthly":
                df = add_all_technicals(get_monthly_data(df))
            elif timeframe.lower() == "weekly":
                df = add_all_technicals(get_weekly_data(df))

            # Pass strategy args to the strategy method and run it
            strategy(df, kwargs=strategy_args)
