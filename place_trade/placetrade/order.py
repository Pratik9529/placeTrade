
import time
from datetime import datetime, timedelta
from iifl import IIFL
import threading
import random
import math

class OrderController:
    def __init__(self,placetrade):
        self.base_url = "https://dataservice.iifl.in/openapi/prod/"
        self.scriplist=placetrade["scriplist"]
        self.users=placetrade["users"]
        self.trades=placetrade["trades"]

    def update_trade_db(self, algo_trade_id, msg, cp):
        print(msg + "@" + str(cp))
        self.trades.update_one({'_id':algo_trade_id},{'$set':{'log':f"{msg} @ {cp}",'exit_price':cp}})
      

    def get_expiry(self, index):
        current_day_of_week = datetime.today().weekday()
        index = index.upper()
        days = {
            "MIDCAPNIFTY": 0,  # Monday
            "FINNIFTY": 1,      # Tuesday

            "BANKNIFTY": 2,     # Wednesday
        }
        day = days.get(index, 3)  # Default to Thursday if the index is not recognized
        if current_day_of_week == day:
            return (datetime.today() + timedelta(days=7)).strftime("%d%b%y").upper()
        days_until_next_day = (day - current_day_of_week + 7) % 7
        next_day_date = (datetime.today() + timedelta(days=days_until_next_day)).strftime("%d%b%y").upper()
        return next_day_date
    

    def buy_order(self, script, script_code, buy_price):
        iifl=IIFL()
        at = 0
        sL = buy_price - 0.01 * buy_price
        t1 = buy_price + 0.01 * buy_price
        t2 = buy_price + 0.02 * buy_price
        t3 = buy_price + 0.03 * buy_price
        t4 = buy_price + 0.04 * buy_price
        target = t1
        trail_price = 1
        data={
                "sL" : sL,
                "t1" : t1,
                "t2" : t2,
                "t3" : t3,
                "t4" : t4,
                "target" : t1,
                "trail_price" : 1
            }

        try:
            trade=self.trades.insert_one({'script':script, 'scriptCode':script_code, 'buyPrice':buy_price, 'data':data,'log':'create'})
            algo_trade_id = trade.inserted_id  # Placeholder for the last inserted ID

            print("Buy order placed @" + script)
            print("data:- SL=>" + str(sL) + " | t1=>" + str(t1) + " | t2=>" + str(t2) + ", | t3=>" + str(t3) + " | t4=>" + str(t4))

            while True:
                cp = iifl.get_option_ltp(self.users.find_one(),script_code)
                # cp=random.uniform(sL-2,t4+5)
                if cp < sL:
                    self.trades.update_one({'_id':algo_trade_id},{'$set':{'log':f"Exit Order Placed @ {cp}",'exit_price':cp,'net_price':cp-buy_price}})
                    print("Exit order placed @" + str(cp))
                    print("Entry: =>" + str(buy_price) + ", Exit:=> " + str(cp) + ", NET :=> " + str(cp - buy_price))
                    break
                elif cp > t1 and cp < t2 and at==0:
                    self.update_trade_db(algo_trade_id, "Target 1 Achieved", cp)
                    sL = buy_price
                    at=1
                elif cp > t2 and cp < t3 and at==1:
                    self.update_trade_db(algo_trade_id, "Target 2 Achieved", cp)
                    sL = t1
                    at=2
                elif cp > t3 and cp < t4 and at==2:
                    self.update_trade_db(algo_trade_id, "Target 3 Achieved", cp)
                    sL = t2
                    at=3
                elif cp > t4 and cp < target and at==3:
                    self.update_trade_db(algo_trade_id, "Target 4 Achieved", cp)
                    sL = t3
                    at=4
                    target = t4 + trail_price
                elif cp > target and at>target:
                    sL = target
                    target = target + trail_price
                    if cp > target:
                        sL = cp - trail_price
                        target = cp + trail_price
                    self.update_trade_db(algo_trade_id, "Price Trailed to cp:-", cp)
                # Implement logic to wait for 1 second
                time.sleep(1/0.5)
                # print(cp)

        except Exception as e:
            raise e

    def ce_order(self, close, index):
        try:
            iifl = IIFL()
            close = math.ceil(close)
            strike_price = close % 100
            expiry_date = self.get_expiry(index)
            script = index.upper() + expiry_date + str(close - strike_price) + "CE"
            script_code = self.scriplist.find_one({'symbol':script},{'token':1,'_id':0})['token']
            current_price = iifl.get_option_ltp(self.users.find_one(),script_code)
            threading.Thread(target=self.buy_order, args=(script,script_code,current_price,)).start()
            
        except Exception as e:
            raise e

    def pe_order(self, close, index):
        try:
            iifl = IIFL()
            close = round(close)
            strike_price = 100 - (close % 100)
            expiry_date = self.get_expiry(index)
            script = index.upper() + expiry_date + str(strike_price + close) + "PE"
            script_code = self.scriplist.find_one({'symbol':script},{'token':1,'_id':0})['token']
            current_price = iifl.get_option_ltp(self.users.find_one(),script_code)
            threading.Thread(target=self.buy_order, args=(script,script_code,current_price,)).start()
            # self.buy_order(script,script_code,current_price)
        except Exception as e:
            raise e
