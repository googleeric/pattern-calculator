import config, csv
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager

client = Client(config.API_Key, config.API_Secret)

# prices = client.get_all_tickers()

# for price in prices:
#     print(price)

csvfile = open('2022_15minutes.csv', 'w', newline='') 
candlestick_writer = csv.writer(csvfile, delimiter=',')

# Open CSV file
with open('exchange.csv', 'w', newline='') as exchange_csvfile:
    exchange_writer = csv.writer(exchange_csvfile)  # Default delimiter is ','
    
    # Fetch exchange symbols
    exchange_info = client.get_exchange_info()
    symbols = exchange_info['symbols']

    # Write symbols correctly
    for symbol in symbols:
        exchange_writer.writerow([symbol['symbol']])  # Wrap symbol in a list


candlesticks = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_15MINUTE, "2022-09-01", "2025-01-01")

for candlestick in  candlesticks:
    candlestick_writer.writerow(candlestick)

csvfile.close()