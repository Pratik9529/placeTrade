import requests
from datetime import datetime
from Crypto.Cipher import AES
import base64
from pbkdf2 import PBKDF2

class IIFL:
    def __init__(self,placetrade):
        self.base_url = "https://dataservice.iifl.in/openapi/prod/"
        self.users=placetrade["users"]

    # Authenticate user into IIFL
    def authenticate(self, user_session_data):
        method = 'POST'
        api_url = self.base_url + "LoginRequest"
        head_array = {
            'appName': user_session_data['appName'],
            'requestCode': "IIFLMarRQLoginForVendor",
            'userId': user_session_data['userId'],
            'password': user_session_data['password'],
            'appVer': "1.0",
            'key': user_session_data['key'],
            'osName': "WEB"
        }
        body_array = {
            'ClientCode': self.encrypt(user_session_data['clientCode']),
            'Password': self.encrypt(user_session_data['clientPass'])
        }
        request_data = {"head": head_array, "body": body_array}
        header_data = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': "fc714d8e5b82438a93a95baa493ff45b"
        }
        session = requests.Session()
        response = session.request(method, api_url, json=request_data, headers=header_data)
        session.close()
        return response

    # Get Last Traded Price
    def get_ltp(self, user_session_data, scrip_code):
        # response = self.authenticate(user_session_data)
        # cookies = response.cookies.get_dict()
        method = 'POST'
        api_url = self.base_url + "MarketFeed"
        header_data = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': "fc714d8e5b82438a93a95baa493ff45b",
            'Cookie': 'IIFLMarcookie=' + user_session_data['IIFLMarcookie']
        }
        head_array = {
            'appName': user_session_data['appName'],
            'password': user_session_data['password'],
            'appVer': "1.0",
            'key': user_session_data['key'],
            'osName': "WEB",
            'userId': user_session_data['userId'],
            'requestCode': "IIFLMarRQMarketFeed"
        }
        body_array = {
            'ClientCode': user_session_data['clientCode'],
            'Count': 1,
            'MarketFeedData': [{
                'Exch': 'N',
                'ExchType': 'c',
                'ScripCode': scrip_code
            }],
            'LastRequestTime': "/Date(" + str(int(datetime.now().timestamp() * 1000)) + ")/"
        }
        request_data = {"head": head_array, "body": body_array}
        # return request_data
        session = requests.Session()
        response = session.request(method, api_url, json=request_data, headers=header_data)
        session.close()
        return response.json()['body']['Data'][0]['LastRate']
    
    def get_option_ltp(self, user_session_data, scrip_code):
        # response = self.authenticate(user_session_data)
        # cookies = response.cookies.get_dict()
        method = 'POST'
        api_url = self.base_url + "MarketFeed"
        header_data = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': "fc714d8e5b82438a93a95baa493ff45b",
            'Cookie': 'IIFLMarcookie=' + user_session_data['IIFLMarcookie']
        }
        head_array = {
            'appName': user_session_data['appName'],
            'password': user_session_data['password'],
            'appVer': "1.0",
            'key': user_session_data['key'],
            'osName': "WEB",
            'userId': user_session_data['userId'],
            'requestCode': "IIFLMarRQMarketFeed"
        }
        body_array = {
            'ClientCode': user_session_data['clientCode'],
            'Count': 1,
            'MarketFeedData': [{
                'Exch': 'N',
                'ExchType': 'D',
                'ScripCode': scrip_code
            }],
            'LastRequestTime': "/Date(" + str(int(datetime.now().timestamp() * 1000)) + ")/"
        }
        request_data = {"head": head_array, "body": body_array}
        # return request_data
        session = requests.Session()
        response = session.request(method, api_url, json=request_data, headers=header_data)
        session.close()
        return response.json()['body']['Data'][0]['LastRate']
    
    def historical_data(self, user_session_data, scrip_code,interval,from_date,to_date):
        # response = self.authenticate(user_session_data)
        # cookies = response.cookies.get_dict()
        request_data = {
        'Exch': 'N',
        'ExchType': 'C',
        'ScripCode': scrip_code,
        'Intervel': interval,
        'from': from_date,
        'end': to_date
    }
        api_url = f"https://dataservice.iifl.in/openapi/prod/historical/{request_data['Exch']}/{request_data['ExchType']}/{request_data['ScripCode']}/{request_data['Intervel']}?from={request_data['from']}&end={request_data['end']}"
        headers = {
        'x-clientcode': user_session_data['clientCode'],
        'x-auth-token': user_session_data['JwtToken'],
        'Ocp-Apim-Subscription-Key': 'fc714d8e5b82438a93a95baa493ff45b',
        'Cookie': 'IIFLMarcookie=' + user_session_data['IIFLMarcookie']
    }
        response = requests.get(api_url, headers=headers)
     # Parse the response JSON
        historical_data = response.json()['data']['candles']
        # Format the historical data
        ohlc_arr = []
        for candle in historical_data:
            ohlc = {
                "timeStamp": candle[0],
                "open": candle[1],
                "high": candle[2],
                "low": candle[3],
                "close": candle[4],
                "volume": candle[5]
            }
            ohlc_arr.append(ohlc)
        return ohlc_arr
    
    def get_funds(self):
        user_session_data=self.users.find_one()
        # response = self.authenticate(user_session_data)
        # cookies = response.cookies.get_dict()
        method = 'POST'
        api_url = self.base_url + "margin"
        header_data = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': "fc714d8e5b82438a93a95baa493ff45b",
            'Cookie': 'IIFLMarcookie=' + user_session_data['IIFLMarcookie']
        }
        head_array = {
            'appName': user_session_data['appName'],
            'password': user_session_data['password'],
            'appVer': "1.0",
            'key': user_session_data['key'],
            'osName': "WEB",
            'userId': user_session_data['userId'],
            'requestCode': "IIFLMarRQMarginV3"
        }
        body_array = {
            'ClientCode': user_session_data['clientCode'],
        }
        request_data = {"head": head_array, "body": body_array}
        session = requests.Session()
        response = session.request(method, api_url, json=request_data, headers=header_data)
        # return response
        session.close()
        return response.json()['body']['EquityMargin'][0]['ALB']
    
    def holdings(self):
        user_session_data=self.users.find_one()
        # response = self.authenticate(user_session_data)
        # cookies = response.cookies.get_dict()
        method = 'POST'
        api_url = self.base_url + "Holding"
        header_data = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': "fc714d8e5b82438a93a95baa493ff45b",
            'Cookie': 'IIFLMarcookie=' + user_session_data['IIFLMarcookie']
        }
        head_array = {
            'appName': user_session_data['appName'],
            'password': user_session_data['password'],
            'appVer': "1.0",
            'key': user_session_data['key'],
            'osName': "WEB",
            'userId': user_session_data['userId'],
            'requestCode': "IIFLMarRQHoldingV2"
        }
        body_array = {
            'ClientCode': user_session_data['clientCode']
        }
        request_data = {"head": head_array, "body": body_array}
        # return request_data
        session = requests.Session()
        response = session.request(method, api_url, json=request_data, headers=header_data)
        session.close()
        return response.json()['body']['Data']

    def encrypt(self, text):
        padded_text = bytes(text+chr(16-len(text) % 16)*(16-len(text) % 16), encoding="utf-8")
        key_gen = PBKDF2('OOIduloZEZhzEL2u0zGfnNvxbB2UR26KoMGTG6Oz0ehtGwlsqgbKYHFgzIastq10', bytes([83, 71, 26, 58, 54, 35, 22, 11,
                         83, 71, 26, 58, 54, 35, 22, 11]))

        aesiv = key_gen.read(16)
        aeskey = key_gen.read(32)
        cipher = AES.new(aeskey, AES.MODE_CBC, aesiv)

        return str(base64.b64encode(cipher.encrypt(padded_text)), encoding="utf-8")
 
    def NFO_order(self,token,ltp,qty,transaction):
        user_session_data=self.users.find_one()
        response = self.authenticate(user_session_data)
        # return response
        cookies = response.cookies.get_dict()
        # return cookies
        method = 'POST'
        api_url = self.base_url + "OrderRequest"
        # return api_url
        header_data = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': "fc714d8e5b82438a93a95baa493ff45b",
            'Cookie': 'IIFLMarcookie=' + cookies['IIFLMarcookie']
        }
        head_array = {
            'appName': user_session_data['appName'],
            'password': user_session_data['password'],
            'appVer': "1.0",
            'key': user_session_data['key'],
            'osName': "WEB",
            'userId': user_session_data['userId'],
            'requestCode': "IIFLMarRQOrdReq"
        }
        body_array = {
            'ClientCode': user_session_data['clientCode'],
            "OrderFor": "P",
            "Exchange": "N",
            "ExchangeType": "D",
            "Price": ltp,
            "OrderID": "1111",
            "OrderType": transaction,
            "Qty": qty,
            "OrderDateTime": "/Date(1563857357612)/",
            "ScripCode": token,
            "AtMarket": True,
            "RemoteOrderID": "s0002201907231019172",
            "ExchOrderID": "0",
            "DisQty": 0,
            "IsStopLossOrder": False,
            "StopLossPrice": 0,
            "IsVTD": False,
            "IOCOrder": False,
            "IsIntraday": False,
            "PublicIP": "192.168.84.215",
            "AHPlaced": "N",
            "ValidTillDate": "/Date(1563857357611)/",
            "iOrderValidity": 0,
            "OrderRequesterCode": user_session_data['clientCode'],
            "TradedQty": 0
        }
        request_data = {"head": head_array, "body": body_array}
        request_data={"_ReqData":request_data,"AppSource":"40377"}
        #  $request = array("_ReqData" => array("head" => $head, "body" => $body), "AppSource" => $clientData->appSource);
        # return request_data
        session = requests.Session()
        # return (method, api_url, request_data, header_data)
        response = session.request(method, api_url, json=request_data, headers=header_data)
        session.close()
        return response
