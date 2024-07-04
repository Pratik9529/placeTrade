import pandas_ta as ta
import pandas as pd
import time
import pymongo
import threading
import getscript as gs

client=pymongo.MongoClient("mongodb://localhost:27017")
db=client["placetrade"]
collection=db["rsi_ema"]
def getData(tickers):
        for ticker in tickers:
            df=pd.DataFrame()
            try:
                df=df.ta.ticker(f"{ticker}.NS",interval="5m",period="60d")
                # print(df)
                # return False
                df["rsi14"]=ta.rsi(df['Close'],length=14)
                df["ema50"]=ta.ema(df['Close'],length=50)
                df["ema200"]=ta.ema(df['Close'],length=200)
                df["ema100"]=ta.ema(df['Close'],length=100)
                df["ticker"]=ticker
                tickerData={
                    "ticker":ticker,
                    "open":df["Open"].iloc[-2],
                    "close":df["Close"].iloc[-2],
                    "high":df["High"].iloc[-2],
                    "low":df["Low"].iloc[-2],
                    "rsi14":df["rsi14"].iloc[-2],
                    "ema50":df["ema50"].iloc[-2],
                    "ema200":df["ema200"].iloc[-2],
                    "ema100":df["ema100"].iloc[-2],
                    "volume":float(df["Volume"].iloc[-2]),
                }                
                # Changed from last row to second last row of df  that means we are getting data of previous complete candle not a live one
                 
                if tickerData["ema50"]!="None":

                    # ema_close_diff=tickerData["close"]-tickerData["ema100"]
                    # if ema_close_diff < 0.005*tickerData["close"] and ema_close_diff >0 and tickerData["rsi14"]<50:
                    # if tickerData["open"]<tickerData["ema100"]<tickerData["close"] and tickerData["rsi14"]>50 :
                    if tickerData["open"]<tickerData["ema50"]<tickerData["close"] :
                        inserted_id = collection.insert_one(tickerData).inserted_id
                        tickerData['_id'] = str(inserted_id)
                        threading.Thread(target=gs.getrade,args=[tickerData["ticker"],tickerData["close"],]).start()
                        # print(tickerData)
            except Exception as e:
                print(e)


def readcsv():    
    csv=pd.read_csv('scriptlist.csv').ticker
    chunk_size=10
    for i in range(0, len(csv), chunk_size):
        chunk = csv[i:i+chunk_size]
        threading.Thread(target=getData,args=[chunk,]).start()  
        time.sleep(5)
def getema():
    # print("running application")
    readcsv()
# getema()
# getData(['COLPAL'])




