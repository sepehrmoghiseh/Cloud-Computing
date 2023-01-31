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
    if rd.exists(os.environ.get('COIN'))==0:
        dic['ids'] = os.environ.get('COIN')
        response = requests.get('https://api.coingecko.com/api/v3/coins/markets', params=dic).json()
        return_response['name'] = os.environ.get('COIN')
        return_response['price'] = response[0]['current_price']
        rd.set(os.environ.get('COIN'),response[0]['current_price'],ex=int(os.environ.get('TIMER')))
        return return_response
    else:
        return_response['name'] =os.environ.get('COIN')
        return_response['price'] = rd.get(os.environ.get('COIN')).decode()
        return return_response





if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True,port=os.environ.get("PORT"))
