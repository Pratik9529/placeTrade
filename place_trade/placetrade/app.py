import final as fi
from datetime import datetime,time,timedelta
from datetime import datetime, time
from iifl import IIFL
import pymongo
# import time

client=pymongo.MongoClient("mongodb://localhost:27017")
db=client["placetrade"]
iifl=IIFL(db)

def is_market_hours():
    current_time = datetime.now().time()
    market_open = time(9, 14)
    market_close = time(15, 31)        
    if market_open <= current_time <= market_close:
        return True
    else:
        print("Market is closed now Please try in Market time")
        return True


def authenticate():
    # Custom username and password
    correct_username = "admin"
    correct_password = "password123"

    # Prompt user for input
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    response=iifl.authenticate(db["users"].find_one())
    response=response.cookies.get_dict()
    db["users"].update_one({"_id":1},{"$set":{"IIFLMarcookie":response["IIFLMarcookie"],"jwtToken":response["JwtToken"]}})
    
    # Check if input matches custom string
    if username == correct_username and password == correct_password:
        print("Authentication successful!")
        # Run your application or code here
        run_application()
    else:
        print("Incorrect username or password. Please try again.")
        # Prompt user to try again
        authenticate()

def run_application():
    # Your application or code logic here
    print("Welcome to the application!")
    while(is_market_hours()):
        #  iifl=iifl()
         fi.getema()
        #  time.sleep(180)
        # print(is_market_hours())
    # Add your application's functionality here

authenticate()
# if __name__ == "__main__":
#     # Call the authenticate function to start the program
#     authenticate()
