import pandas as pd
import pandas_ta as ta
import numpy as np
import itertools


# 1. Reading df + Set index
def read_df():
    df = pd.read_csv("./Binance_BTCUSDT_1min.csv")
    df = df.iloc[:,:6]
    df.columns=['Date','Open', 'High', 'Low', 'Close', 'Volume']
    df.reset_index(drop=True, inplace=True)
    df.Date = pd.to_datetime(df.Date)
    df = df.set_index("Date")
    return df

# 2. resample the df

def resample_df(df, timeframe):
    resampled_open = df.Open.resample(timeframe).first()
    resampled_high = df.High.resample(timeframe).max()
    resampled_low = df.Low.resample(timeframe).min()
    resampled_close = df.Close.resample(timeframe).last()
    resampled_volume = df.Volume.resample(timeframe).sum()
    new_df = pd.concat([resampled_open, resampled_high, resampled_low, resampled_close, resampled_volume], axis=1)
    new_df.dropna(inplace=True)
    return new_df

#Shift open price for convenient use in the same row

def calc_price(new_df):
    new_df["price"] = new_df.Open.shift(-1)

#Hardcode the required indicators

def calc_vol_avg(new_df, x):
    new_df["volma"] = new_df.Volume.rolling(x).mean()
def calc_vwap(new_df, anchor_period):
    new_df['VWAP'] = ta.vwap(new_df.High, new_df.Low, new_df.Close, new_df.Volume, anchor=anchor_period)
def calc_ma(new_df, m, n, o):
    new_df[f'SMA{m}'] = new_df.Close.rolling(m).mean()
    new_df[f'SMA{n}'] = new_df.Close.rolling(n).mean()
    new_df[f'SMA{o}'] = new_df.Close.rolling(o).mean()
def calc_rsi(new_df, l):
    new_df[f'RSI{l}'] = ta.rsi(new_df)

#Hardcode the buysignals

def calc_buy_signal(new_df, vol_ratio):
    new_df["buy_signal"] = np.where(((new_df.Close<new_df.VWAP) & (new_df.Volume>new_df.volma*vol_ratio) & (new_df.Close<new_df.Close.shift(1))), True, False)

#Run the backtest

def backtest(timeframe, anchor_period, x, vol_ratio, tp, sl):
    
    df = read_df()
    new_df = resample_df(df, timeframe)
    calc_vwap(new_df, anchor_period)
    calc_vol_avg(new_df, x)
    calc_price(new_df)
    calc_buy_signal(new_df, vol_ratio)
    new_df.dropna(inplace=True)
    
    #Error handle for no buy signals
    if len(new_df[new_df.buy_signal > 0]) < 1:
        empty_result = pd.DataFrame({
            "entry_time": [0],
            "entry_price": [0],
            "tp_target": [0],
            "sl_target": [0],
            "exit_time": [0],
            "exit_price": [0],
            "pnl": [0]
        })
        amount = 0
        winrate = 0
        pnl = 0
        #return amount, winrate, pnl
        return empty_result
    
    in_position = False
    trades = []
    current_trade = {}
            
    for i in range(len(new_df)-1):
    #Check exit conditions
        if in_position:
            if new_df.iloc[i].Low < current_trade["sl_price"]:
                current_trade["exit_price"] = current_trade["sl_price"]
                pnl = sl - 1
                trades.append({
                    "entry_time":current_trade["entry_time"],
                    "entry_price":current_trade["entry_price"],
                    "tp_target":current_trade["tp_price"],
                    "sl_target":current_trade["sl_price"],
                    "exit_time":new_df.iloc[i].name,
                    "exit_price":current_trade["sl_price"],
                    "pnl": pnl
                })
                current_trade = {}
                in_position = False

            elif new_df.iloc[i].High > current_trade["tp_price"]:
                current_trade["exit_price"] = current_trade["tp_price"]
                pnl = tp - 1
                trades.append({
                    "entry_time":current_trade["entry_time"],
                    "entry_price":current_trade["entry_price"],
                    "tp_target":current_trade["tp_price"],
                    "sl_target":current_trade["sl_price"],
                    "exit_time":new_df.iloc[i].name,
                    "exit_price":current_trade["tp_price"],
                    "pnl":pnl,
                })
                current_trade = {}
                in_position = False

        #Check entry conditions
        if not in_position:
            if new_df.iloc[i].buy_signal == True:
                current_trade["entry_price"] = new_df.iloc[i].price
                current_trade["entry_time"] = new_df.iloc[i+1].name
                current_trade["tp_price"] = new_df.iloc[i].price*tp
                current_trade["sl_price"] = new_df.iloc[i].price*sl
                in_position = True
                
    data = pd.DataFrame(trades)
    amount = len(data)
    winrate = len(data.loc[data.pnl.values>0])/len(data)*100
    pnl = sum(pd.Series(data.pnl))
    #return amount, winrate, pnl
    print(data)
    return data

#Return a series of trades & winrate, amount of trades and pnl

#result = backtest("1H", "W", 50, 3, 1.02, 0.97)
#print(result)
