from binance.client import Client
import csv
import datetime

# Initialize Binance client (replace with your API keys)
api_key = "your_api_key"
api_secret = "your_api_secret"
client = Client(api_key, api_secret)

# Define time range
start_date = "2025-01-01"
interval = Client.KLINE_INTERVAL_15MINUTE  # You can change this to 1m, 1h, etc.

# Get all trading pairs
exchange_info = client.get_exchange_info()
symbols = [symbol['symbol'] for symbol in exchange_info['symbols']]

# Function to fetch and save historical data
def fetch_and_save(symbol):
    print(f"Fetching data for {symbol}...")
    
    klines = client.get_historical_klines(symbol, interval, start_date)

    if not klines:
        print(f"No data found for {symbol}, skipping...")
        return

    # Define CSV file name (e.g., BTCUSDT.csv, ETHUSDT.csv)
    filename = f"{symbol}.csv"

    # Save data in CSV format
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Time", "Open", "High", "Low", "Close", "Volume"])  # Header
        
        for kline in klines:
            time = datetime.datetime.fromtimestamp(kline[0] / 1000)  # Convert timestamp to human-readable date
            open_price = kline[1]
            high = kline[2]
            low = kline[3]
            close = kline[4]
            volume = kline[5]
            
            writer.writerow([time, open_price, high, low, close, volume])

    print(f"Saved {symbol} data to {filename}")

# Loop through all symbols and fetch data
for symbol in symbols:
    fetch_and_save(symbol)

print("All data downloaded successfully!")
