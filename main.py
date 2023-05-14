import json

import quart
import quart_cors
from quart import request

API_KEY = ''
SECRET_KEY = ''
BASE_URL = 'https://paper-api.alpaca.markets'  # use the paper trading URL for testing

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# Keep track of todo's. Does not persist if Python session is restarted.

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")
    
@app.post("/stockprice")
async def historical():
    data = await request.get_json()
    symbol = data['symbol']
    startDate = data['startDate']
    endDate = data['endDate']

    return get_historical_data(symbol, startDate, endDate)

from alpaca.data import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
from alpaca.data.enums import Adjustment
from alpaca.data.timeframe import TimeFrameUnit
from alpaca.data.timeframe import TimeFrame

import pandas as pd
from datetime import datetime


def get_historical_data(symbol: str, startDate: str, endDate: str):
    # Set start and end date for the stock data
    # The Alpaca API requires the start and end date to be in the format YYYY-MM-DD

    # no keys required.
    # keys required
    stock_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

    request_params = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Day,
        start=datetime.strptime(startDate, '%Y-%m-%d'),
        end=datetime.strptime(endDate, '%Y-%m-%d'),
        limit=1
    )

    barset = stock_client.get_stock_bars(request_params)

    # print(barset.df)
    #return barset as a json object following openapi.yaml
    return barset.df.to_json(orient='records')

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
