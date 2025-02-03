from flask import Flask, render_template, jsonify, request
import config, csv
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import datetime
import concurrent.futures
from flask_caching import Cache
# import os

app = Flask(__name__)

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

@app.route('/buy')
def hello():
    return 'Hello, World'

def fetch_candlestick(symbol):
    """ Fetch historical data for a single symbol and remove empty results """
    try:
        start_date = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        # Get today's date
        today = datetime.datetime.now()

        # Add one day to today's date
        end_date = (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        interval = Client.KLINE_INTERVAL_15MINUTE

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
        all_symbols = [s['symbol'] for s in exchange_info['symbols'] if s['symbol'].endswith('USDT')][:100]

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