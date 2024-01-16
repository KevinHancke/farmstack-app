import pandas as pd
from datetime import timedelta, datetime
from binance.client import Client
from dotenv import load_dotenv
import os
from tqdm import tqdm

#Get environment variables from .env
load_dotenv(".env")
api_key: str = os.getenv("binance_api_key")
api_secret: str = os.getenv("binance_api_secret")

#Instantiate Binance Client
client = Client(api_key, api_secret)

#Function for getting data using Python wrapper for Binance Rest API. Returns a frame to be used in get_new_rows()
def get_binance_data(symbol, start):
    frame = pd.DataFrame(client.get_historical_klines(symbol, '1m', str(start)))
    frame.columns = ["timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_av", "trades", "tb_base_av", "tb_quote_av", "ignore"]
    frame.set_index("timestamp", inplace=True)
    frame.index = pd.to_datetime(frame.index, unit="ms")
    frame = frame.astype(float)
    print("Getting data from websocket/historical kline and returning dataframe")
    return frame

#Check the sql database for latest date and compares the index of the dataframe returned by get_binance_data(). It returns only the necessary rows to be appended.
def get_new_rows(engine):
    df = get_binance_data("BTCUSDT", pd.to_datetime("today")-timedelta(3))
    max_date_str = pd.read_sql("SELECT MAX(timestamp) FROM binance_btcusdt_1m", engine).values[0][0]
    max_date_timestamp = pd.to_datetime(max_date_str, utc=df.index.tzinfo)
    new_rows = df[df.index> max_date_timestamp]
    print("Getting new rows, comparing dates")
    return new_rows

#Append the necessary new_rows to the sql DB as determined by the get_new_rows() function
def append_new_rows(engine):
    new_rows = get_new_rows(engine)
    new_rows.to_sql("binance_btcusdt_1m", engine, if_exists="append")
    print(str(len(new_rows)) + "rows have been imported")