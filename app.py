from flask import Flask, render_template, jsonify, request
import requests
# import config, csv
from binance.client import Client
import datetime
import concurrent.futures
from flask_caching import Cache
from flask_cors import CORS
import yfinance as yf
import pytz  # For timezone conversion
import pandas as pd
from dateutil import parser as date_parser
# import os

app = Flask(__name__)

# Enable CORS for all routes and origins
CORS(app)

# Flask Cache Configuration (Stores data for 10 minutes)
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 600  # 10 minutes
cache = Cache(app)

# Load API keys from environment variables
# API_KEY = os.getenv("BINANCE_API_KEY")
# API_SECRET = os.getenv("BINANCE_API_SECRET")

# Initialize Binance client (replace with your API keys)
API_Key = "R6OJdBchvnp9USShft9EM6NmrMyDlyzuMwrNzZXnJ39MRGhBWD6efmD9BN4ImQws"
API_Secret = "HiHgLLyox4SuESXoUANRc5JcpGoOeLB4g1bra7OmfKyQqN7bn49VhF8lLC6GZWFJ"

# if not API_KEY or not API_SECRET:
#     raise ValueError("Missing Binance API credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET as environment variables.")

# client = Client(API_KEY, API_SECRET)

client = Client(API_Key, API_Secret)

@app.route('/')
def index():

    # exchange_info = client.get_exchange_info()
    # symbols = exchange_info['symbols']

    # allSymbols = [{"exchange": symbol['symbol']} for symbol in symbols if symbol['symbol'].endswith('USDT')]

    # # Write to CSV only once
    # with open('data/exchange_list.csv', 'w', newline='') as csvfile:
    #     fieldnames = ['exchange']
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #     writer.writeheader()
    #     writer.writerows(allSymbols)  # Write all symbols at once
#helloworld


    return  render_template('index.html')

@app.route('/stock')
def stock():
    return render_template('stock.html')

@app.route('/buy')
def hello():
    return 'Hello, World'

def fetch_candlestick(symbol):
    """ Fetch historical data for a single symbol and remove empty results """
    try:
        start_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        # Get today's date
        today = datetime.datetime.now()

        # Add one day to today's date
        end_date = (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        interval = Client.KLINE_INTERVAL_5MINUTE

        candlesticks = client.get_historical_klines(symbol, interval, start_date, end_date)

        if not candlesticks:  # Skip if no data
            return None

        processed_data = [
            {"time": data[0] / 1000, "open": data[1], "high": data[2], "low": data[3], "close": data[4]}
            for data in candlesticks
        ]

        return {
            'symbol': symbol,
            'candlesticks': processed_data
        }

    except Exception as e:
        return None  # Skip cryptos that cause errors


@app.route('/history')
@cache.cached(timeout=600)  # Cache results for 10 minutes
def history():
    try:
        exchange_info = client.get_exchange_info()
        all_symbols = [s['symbol'] for s in exchange_info['symbols'] if s['symbol'].endswith('USDT')][:20]

        all_candlesticks = {}

        # Fetch data in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(fetch_candlestick, all_symbols)

        # Filter out None (empty) results
        for result in results:
            if result:  # Only add valid data
                symbol = result['symbol']
                candlesticks = result['candlesticks']
                all_candlesticks[symbol] = candlesticks  # Store the candlesticks for each symbol

        return jsonify(all_candlesticks)  # Return the entire `all_candlesticks` dictionary

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/scanner')
def scanner():
    return render_template('scanner.html')


# @app.route('/indian-stock')
# def indianStock():

#     try:
#         # Fixed list of stock symbols (this is now static on the backend)
#         symbols = ["RELIANCE.NS",]
#         # Get today's and yesterday's date
#         today = datetime.datetime.today().strftime("%Y-%m-%d")
#         yesterday = (datetime.datetime.today() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")

#         # Result container for all stocks
#         all_stock_data = {}

#         # Loop through each symbol to fetch stock data
#         for symbol in symbols:
#             stock = yf.Ticker(symbol)
#             data = stock.history(start=yesterday, end=today, interval="5m")

#             if data.empty:
#                 data = stock.history(period="2d", interval="5m")

#             if data.empty:
#                 all_stock_data[symbol] = {"error": "No stock data available."}
#                 continue  # Skip to next symbol if no data

#             # Convert index (UTC) to IST
#             ist = pytz.timezone("Asia/Kolkata")
#             data.index = data.index.tz_convert(ist)

#             # Convert index to column but keep timezone
#             data.reset_index(inplace=True)
#             data.rename(columns={"index": "Datetime"}, inplace=True)

#             # Ensure 'Datetime' is in IST and remains a datetime object
#             data["Datetime"] = pd.to_datetime(data["Datetime"]).dt.tz_localize(None)

#             # Convert DataFrame to JSON (compatible with Lightweight Charts)
#             chart_data = [
#                 {
#                     "time": int(row.Datetime.timestamp()),  # Now in IST, no timezone issues
#                     "open": row.Open,
#                     "high": row.High,
#                     "low": row.Low,
#                     "close": row.Close
#                 }
#                 for row in data.itertuples()
#             ]

#             all_stock_data[symbol] = chart_data

#         return jsonify(all_stock_data)

#     except Exception as e:
#         print(f"Error: {e}")  # Debugging error in console
#         return jsonify({"error": str(e)}), 500


@app.route('/indian-stock')
def indianStock():
    try:
        ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIyVUJTTE4iLCJqdGkiOiI2ODFiN2IyNzJiOGNkZjUwMTEwMzJlYTciLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc0NjYzMTQ2MywiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzQ2NjU1MjAwfQ.oryOKEVeKEXjAk1sZJLXdpQyKGtcsa-1bZ_38zRJ29A'
        
        INSTRUMENT_KEYS = [
            "NSE_EQ|INE002A01018", # RELIANCE
            "NSE_EQ|INE018A01030", # LT
            "NSE_EQ|INE040A01034", # HDFCBANK
            "NSE_EQ|INE467B01029", # TCS
            "NSE_EQ|INE062A01020", # SBIN
            "NSE_EQ|INE259A01022", # COLPAL
            "NSE_EQ|INE238A01034", # AXISBANK
            "NSE_EQ|INE860A01027", # HCLTECH
            "NSE_EQ|INE003A01024", # SIEMENS
            "NSE_EQ|INE245A01021", # TATAPOWER
            "NSE_EQ|INE669C01036", # TECHM
            "NSE_EQ|INE154A01025", # ITC
            "NSE_EQ|INE102D01028", # GODREJCP
            "NSE_EQ|INE917I01010", # BAJAJ-AUTO
            "NSE_EQ|INE768C01010", # ZYDUSWELL
            "NSE_EQ|INE528G01035", # YESBANK
            "NSE_EQ|INE575P01011", # STARHEALTH
            "NSE_EQ|INE766P01016", # MAHLOG
            "NSE_EQ|INE358U01012", # ZOTA
            "NSE_EQ|INE666D01022", # BOROSIL RENEWABLES LTD
            "NSE_EQ|INE397D01024", # BHARTIARTL
            "NSE_EQ|INE090A01021", # ICICIBANK
            "NSE_EQ|INE009A01021", # INFY
            "NSE_EQ|INE030A01027", # HINDUNILVR
            "NSE_EQ|INE0J1Y01017", # LICI
            "NSE_EQ|INE101A01026", # M&M
            "NSE_EQ|INE213A01029", # ONGC
            "NSE_EQ|INE752E01010", # POWERGRID
            "NSE_EQ|INE742F01042", # ADANIPORTS
            "NSE_EQ|INE423A01024", # ADANIENT
            "NSE_EQ|INE155A01022", # TATAMOTORS
            "NSE_EQ|INE081A01020", # TATASTEEL
            "NSE_EQ|INE205A01025", # VEDL
            "NSE_EQ|INE242A01010", # IOC
            "NSE_EQ|INE814H01011", # ADANIPOWER
            "NSE_EQ|INE522F01014", # COALINDIA
        ]

        unit = "minutes"
        interval = "5"
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {ACCESS_TOKEN}'
        }
        ist = pytz.timezone("Asia/Kolkata")
        all_stock_data = {}

        today = datetime.datetime.today().strftime("%Y-%m-%d")
        yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        # yesterday = '2025-05-09'

        for key in INSTRUMENT_KEYS:

            # url = f"https://api.upstox.com/v3/historical-candle/{key}/{unit}/{interval}/{today}/{yesterday}"

            url = f"https://api.upstox.com/v3/historical-candle/intraday/{key}/{unit}/{interval}"
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                result = response.json()

                candles = result.get("data", {}).get("candles", [])
                if not candles:
                    all_stock_data[key] = {"error": "No data"}
                    continue

                chart_data = []
                for candle in candles:
                    time_str, open_, high, low, close, *_ = candle
                    dt = date_parser.isoparse(time_str)           # Parse ISO string
                    dt_ist = dt.astimezone(ist).replace(tzinfo=None)  # Convert to IST, then remove tz
                    timestamp = int(dt_ist.timestamp()) 

                    chart_data.append({
                        "time": timestamp,
                        "open": open_,
                        "high": high,
                        "low": low,
                        "close": close
                    })

                all_stock_data[key] = chart_data

            except Exception as e:
                all_stock_data[key] = {"error": str(e)}

        return jsonify(all_stock_data)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500