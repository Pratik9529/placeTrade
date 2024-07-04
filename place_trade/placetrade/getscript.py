import pandas_ta as ta
import pandas as pd
import time
import pymongo
import threading
from order import OrderController
from iifl import IIFL
import random
from datetime import datetime, timedelta

client=pymongo.MongoClient("mongodb://localhost:27017")
db=client["placetrade"]
collection=db["scriplist"]
transaction=db["transaction"]
iifl=IIFL(db)
order=OrderController(db)
trades=db["trades"]
current_date = pd.Timestamp.now(tz='Asia/Kolkata').date().isoformat()  # Current date in the local timezone (Asia/Kolkata)
# print(current_date)

def last_thursday_of_month():
    today = datetime.today()
    year = today.year
    month = today.month
    
    # Calculate the last day of the current month
    last_day_of_month = datetime(year, month, 1) + timedelta(days=32)
    last_day_of_month = last_day_of_month.replace(day=1) - timedelta(days=1)
    
    # Find the last Thursday of the current month
    last_thursday = last_day_of_month - timedelta(days=(last_day_of_month.weekday() - 3) % 7)
    
    # If today is greater than the last Thursday of the current month, 
    # find the last Thursday of the next month
    if today > last_thursday:
        # Move to the next month
        month += 1
        if month > 12:
            month = 1
            year += 1
        
        # Calculate the last day of the next month
        last_day_of_next_month = datetime(year, month, 1) + timedelta(days=32)
        last_day_of_next_month = last_day_of_next_month.replace(day=1) - timedelta(days=1)
        
        # Find the last Thursday of the next month
        last_thursday = last_day_of_next_month - timedelta(days=(last_day_of_next_month.weekday() - 3) % 7)
    
    # Format the date as "30MAY2024"
    formatted_date = last_thursday.strftime("%d%b%Y").upper()
    
    return formatted_date
    # return "30MAY2024"

def buy_order(symbol,qty,token,name):
   
    try:
        ltp=float(iifl.get_option_ltp(db["users"].find_one(),token))
    except:
        ltp=float(iifl.get_option_ltp(db["users"].find_one(),token))
    # finally:
    #     return False
    qty=int(qty)
    sl=ltp-ltp*0.01
    target=ltp+ltp*0.02
    turnover=ltp*qty
    brokerage=( turnover *0.0495/100) + ( turnover *0.0001/100) + ( turnover *0.003/100)+ ( turnover *0.0015/100)
    brokerage=brokerage+20
    brokerage=brokerage+brokerage*18/100

    amount1=db["users"].find_one()["amount"]
    if (ltp*qty)>amount1:
        print(f"Low Capital , {symbol} will not execute")
        # trades.update_one({"_id": trade.inserted_id},{"$set": {"active": 0,"message":"Low Funds in account",}})
        return False
    trade=trades.insert_one({
        "symbol":symbol,
        "name":name,
        "qty":qty,
        "token":token,
        "buy_Price":ltp,
        "stopLoss":sl,
        "target":target,
        # "date":current_date,  
        "current_date":current_date,
        "entry_brokerage":brokerage,
        "active":1
    })
    amount2=amount1-ltp*qty-brokerage
    transaction.insert_one({"symbol":symbol,"Debit":amount1-amount2,"Balance":amount2})
    # iifl.NFO_order(token,ltp,qty,'BUY')      # Exceute order on broker
    
    print(f"Buy {symbol} @ Rs {ltp} @ {qty }qty @ sl {sl} @target  {target} ")
    buy_price=ltp
    
    db["users"].update_one({"_id":1},{"$set":{"amount":amount2}})
    while True:
        try:
            ltp=float(iifl.get_option_ltp(db["users"].find_one(),token))
        except:
            ltp=float(iifl.get_option_ltp(db["users"].find_one(),token))

        # finally:
        #     return False
        # ltp=float(random.uniform(sl-1,target+2)) 

        if(ltp<=sl):
            net=ltp-buy_price
            loss=qty*net

            turnover=ltp*qty
            brokerage=( turnover *0.0495/100) + ( turnover *0.0001/100) + ( turnover *0.003/100)+ ( turnover *0.0015/100)+ ( turnover *0.0625/100)
            brokerage=brokerage+20
            brokerage=brokerage+brokerage*18/100

            # iifl.NFO_order(token,ltp,qty,'SELL')      # SELL order on broker
            trades.update_one({"_id": trade.inserted_id},{"$set": {"active": 0,"message":"SL Hit","exit":ltp,"net":net,"loss":loss,"exit_brokerage":brokerage}})
            amount1=db["users"].find_one()["amount"]
            amount2=amount1+ltp*qty-brokerage
            transaction.insert_one({"symbol":symbol,"Credit":amount2-amount1,"Balance":amount2})
            db["users"].update_one({"_id":1},{"$set":{"amount":amount2}})
            print(f"{symbol} Trade Exit SL Hit")
            break

        if(ltp>=target):
            net=ltp-buy_price
            profit=qty*net

            turnover=ltp*qty
            brokerage=( turnover *0.0495/100) + ( turnover *0.0001/100) + ( turnover *0.003/100)+ ( turnover *0.0015/100)+ ( turnover *0.0625/100)
            brokerage=brokerage+20
            brokerage=brokerage+brokerage*18/100

            # iifl.NFO_order(token,ltp,qty,'SELL')      # SELL order on broker
            trades.update_one({"_id": trade.inserted_id},{"$set": {"active": 0,"message":"Target Hit","exit":ltp,"net":net,"profit":profit,"exit_brokerage":brokerage}})
            amount1=db["users"].find_one()["amount"]
            amount2=amount1+ltp*qty-brokerage

            transaction.insert_one({"symbol":symbol,"Credit":amount2-amount1,"Balance":amount2})
            db["users"].update_one({"_id":1},{"$set":{"amount":amount2}})
            print(f"{symbol} Trade Exit Target Hit")
            break
        time.sleep(5)        

def getrade(name="",close=0):
    trade=collection.find({
            "name": name,
            "strike": {
                "$lte": f"{close}.000000"
            },
           "symbol":{
                "$regex":"CE$"
            },
            "expiry":{
                "$eq":last_thursday_of_month()
            },
            "exch_seg":{
                "$eq":"NFO"
            }
            }).sort({"strike": -1}).limit(1)
    for t in trade:       
         active=trades.find_one({"name":name, 
                                # "$or": [
                                #         {"active": 1},
                                #         {"message": "Target Hit"}
                                #     ]
                                 })
         if active:
            #  print(f"{t['symbol']} This Trade Already Active")
             return False
         else:
            threading.Thread(target=buy_order,args=[t["symbol"],t["lotsize"],t["token"],name]).start()

# getrade()
# buy_order('SBIN30MAY24800CE',100,136076)