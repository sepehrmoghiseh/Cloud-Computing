import requests
from flask import Flask
import redis
import os
import json
dic = {}
dic['vs_currency'] = 'usd'
rd = redis.Redis(host='test', port=6379)
app = Flask(__name__)
f = open('config.json')
data=json.load(f)


@app.route('/' ,methods=['get'])
def getAd():
    return_response = {}
    if rd.exists(data['COIN'])==0:
        dic['ids'] = data['COIN']
        response = requests.get('https://api.coingecko.com/api/v3/coins/markets', params=dic).json()
        return_response['name'] = data['COIN']
        return_response['price'] = response[0]['current_price']
        rd.set(data['COIN'],response[0]['current_price'],ex=int(data['TIMER']))
        return return_response
    else:
        return_response['name'] =data['COIN']
        return_response['price'] = rd.get(data['COIN']).decode()
        return return_response





if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True,port=data['PORT'])
