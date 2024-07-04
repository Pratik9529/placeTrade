import pandas_ta as ta
import pandas as pd
def detect_pivot_candles(df):
    pivots = []
    for i in range(2, len(df) - 2):
        # Bearish reversal: Shooting Star or Hanging Man
        if df['Close'][i] > df['Open'][i] and df['Close'][i] >= df['High'][i-1] and df['Close'][i] > df['High'][i+1]:
            pivots.append((df[i], 'Bearish Reversal'))
        # Bullish reversal: Hammer or Inverted Hammer
        elif df['Close'][i] < df['Open'][i] and df['Low'][i] <= df['Low'][i-1] and df['Low'][i] < df['Low'][i+1]:
            pivots.append((df[i], 'Bullish Reversal'))
    return pivots

# Example usage:
# data = mpf.sample_data.get_sample_data()
df=pd.DataFrame()
# df = mpf.sample_data.parse(data, column_names=('Date', 'Open', 'High', 'Low', 'Close', 'Volume'), index_col=0)
df=df.ta.ticker("WIPRO.NS",interval="1d",period="60d")
print(df)
# return False
# pivots = detect_pivot_candles(df)
# print("Pivot Candles:", pivots)
