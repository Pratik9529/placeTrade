from iifl import IIFL
import pymongo
import pandas as pd
import time as t
from datetime import datetime,time,timedelta
from order import OrderController
class Index:
    def __init__(self,placetrade):
        self.db=placetrade
    def checkCandle(self,candle):
        close=candle.close[0]
        open=candle.open[0]
        low=candle.low[0]
        high=candle.high[0]
        high_low_diff=abs(high-low)
        open_close_diff=abs(open-close)
        candle_percentage=(open_close_diff/high_low_diff)*100
        if open<close:
            print(f"Bullish {candle_percentage}%")
        else :
            print(f"Bearish {candle_percentage}%")
        
    def is_market_hours():
        current_time = datetime.now().time()
        market_open = time(9, 15)
        market_close = time(15, 31)  
       
        if market_open >= current_time >= market_close:
            # return "True"
            print("True")
        else:
            print("False")
            # return "False"
    
    def nifty(self):
        iifl=IIFL()
        order=OrderController(self.db)
        nifty_historical_1m=self.db["nifty_historical_1m"]
        user=self.db.users.find_one()
        current_time = datetime.now().time()
        market_open = time(9, 15)
        market_close = time(15, 31)  
        while market_open <= current_time <= market_close:   
            response=iifl.historical_data(user,999920000,'3m','2024-03-1',datetime.now().date()+timedelta(days=1))
            # return response
            nifty_historical_1m.insert_one(response[len(response)-1])
            data=pd.DataFrame(response)
            ema_10=self.ema(data.close,10)
            ema_25=self.ema(data.close,25)
            last_close=data.close[len(data.close)-1]            
            if ema_25<ema_10:
                if last_close>ema_10:
                    order.ce_order(last_close,"NIFTY")
                    break
            else:
                if last_close<ema_10:
                    order.pe_order(last_close,"NIFTY")
                    break
                 
    
    def banknifty(self):
        iifl=IIFL()
        order=OrderController(self.db)
        banknifty_historical_1m=self.db["banknifty_historical_1m"]
        user=self.db.users.find_one()
        current_time = datetime.now().time()
        market_open = time(9, 15)
        market_close = time(15, 31)  
        while market_open <= current_time <= market_close:   
            response=iifl.historical_data(user,999920005,'3m','2024-03-1',datetime.now().date()+timedelta(days=1))
            banknifty_historical_1m.insert_one(response[len(response)-1])
            data=pd.DataFrame(response)
            ema_10=self.ema(data.close,10)
            ema_25=self.ema(data.close,25)
            last_close=data.close[len(data.close)-1]          
            if ema_25<ema_10:
                  if last_close>ema_10:
                    order.ce_order(data.close[len(data.close)-1],"BANKNIFTY")
                    break
            else:
                  if last_close<ema_10:
                    order.pe_order(data.close[len(data.close)-1],"BANKNIFTY")
                    break
                
            candle=pd.DataFrame(response[-1:])
            # self.checkCandle(candle)
            # t.sleep(50)


    def sma(self,indices="NIFTY",length=50):
        if indices=="NIFTY":
            data=self.db.nifty_historical_1m.find()
        else:
             data=self.db.banknifty_historical_1m.find()
        close=pd.DataFrame(data).close
        close=close[-length:]
        close_sum=sum(close)
        sma=close_sum/length
        return sma
    
    def ema(self,close,length=20):
        ema_values = []
        sma = sum(close[:length]) / length
        ema_values.append(sma)
        multiplier = 2 / (1 + length)
        for i in range(length, len(close)):
            ema = (close[i] - ema_values[-1]) * multiplier + ema_values[-1]
            ema_values.append(ema)
        # print(ema_values[-1])
        return ema_values[-1]
    
