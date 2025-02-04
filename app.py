import os
import csv
import datetime
import concurrent.futures
from flask import Flask, render_template, jsonify
from flask_caching import Cache
from flask_cors import CORS
from binance.client import Client

app = Flask(__name__)

# Enable CORS
CORS(app)

# Flask Cache (stores data for 10 minutes)
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 600  # 10 minutes
cache = Cache(app)

# Binance API Keys
API_Key = "R6OJdBchvnp9USShft9EM6NmrMyDlyzuMwrNzZXnJ39MRGhBWD6efmD9BN4ImQws"
API_Secret = "HiHgLLyox4SuESXoUANRc5JcpGoOeLB4g1bra7OmfKyQqN7bn49VhF8lLC6GZWFJ"
client = Client(API_Key, API_Secret)

# Directory to store CSV files
DATA_DIR = "crypto_data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_csv_filename(symbol):
    """ Returns the CSV filename for a given symbol """
    return os.path.join(DATA_DIR, f"{symbol}.csv")

def is_recent_file(filepath, max_age_seconds=600):
    """ Checks if a file is recent (within max_age_seconds) """
    if not os.path.exists(filepath):
        return False
    file_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
    return file_age.total_seconds() < max_age_seconds

def fetch_candlestick(symbol):
    """ Fetch and save historical data for a symbol """
    csv_file = get_csv_filename(symbol)

    # If recent CSV exists, read from it
    if is_recent_file(csv_file):
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            return {
                "symbol": symbol,
                "candlesticks": [row for row in reader]
            }

    try:
        # Fetch fresh data from Binance
        start_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        interval = Client.KLINE_INTERVAL_15MINUTE

        candlesticks = client.get_historical_klines(symbol, interval, start_date, end_date)

        if not candlesticks:
            return None  # Skip if no data

        processed_data = [
            {
                "time": data[0] / 1000, 
                "open": data[1], 
                "high": data[2], 
                "low": data[3], 
                "close": data[4]
            }
            for data in candlesticks
        ]

        # Save to CSV
        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["time", "open", "high", "low", "close"])
            writer.writeheader()
            writer.writerows(processed_data)

        return {
            "symbol": symbol,
            "candlesticks": processed_data
        }

    except Exception as e:
        return None  # Skip errors


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/history')
@cache.cached(timeout=600)  # Cache for 10 minutes
def history():
    try:
        exchange_info = client.get_exchange_info()
        all_symbols = [s['symbol'] for s in exchange_info['symbols'] if s['symbol'].endswith('USDT')][:600]

        all_candlesticks = {}

        # Fetch data in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(fetch_candlestick, all_symbols)

        for result in results:
            if result:
                symbol = result['symbol']
                all_candlesticks[symbol] = result['candlesticks']

        return jsonify(all_candlesticks)

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/scanner')
def scanner():
    return render_template('scanner.html')


if __name__ == '__main__':
    app.run(debug=True)
