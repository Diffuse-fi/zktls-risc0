import requests
import json
import sys

# Define the Binance API endpoint and symbol
BASE_URL = "https://api.binance.com"

# Function to fetch the full list of trading pairs
def get_all_symbols():
    endpoint = f"{BASE_URL}/api/v3/exchangeInfo"
    response = requests.get(endpoint)

    # Check for successful response
    if response.status_code == 200:
        data = response.json()
        symbols = [s['symbol'] for s in data['symbols'] if s['status'] == 'TRADING']
        return symbols
    else:
        print("Error fetching data:", response.status_code, response.text)
        return None

# Function to fetch current prices and timestamps for multiple symbols
def get_current_prices_with_timestamp(symbols):
    endpoint = f"{BASE_URL}/api/v3/ticker/24hr"
    symbols_param = json.dumps(symbols, separators=(',', ':'))
    # params = {"symbols": '["ETHBTC","ETHUSDT","ETHUSDC","BTCUSDT"]'}
    params = {"symbols": symbols_param, "type": "MINI"}
    print ("Params: ", params)
    response = requests.get(endpoint, params=params)

    # Check for successful response
    if response.status_code == 200:
        data = response.json()

        # Write the entire response to a JSON file
        with open('response.json', 'w') as file:
            json.dump(data, file, indent=4)
        print("Full response saved to response.json")

        # Filter the data for the desired symbols and include the price and timestamp
        stripped_prices = {
            item['symbol']: {
                "price": float(item['lastPrice']),
                "closeTime": item['closeTime']
            } for item in data if item['symbol'] in symbols
        }

        # Write the filtered prices with timestamp to another JSON file
        with open('stripped_prices.json', 'w') as file:
            json.dump(stripped_prices, file, indent=4)
        print("Filtered prices saved to stripped_prices.json")

        return stripped_prices
    else:
        print("Error fetching data:", response.status_code, response.text)
        return None

# Get and print the full list of trading pairs
all_symbols = get_all_symbols()
if all_symbols:
    print("Available trading pairs on Binance:")
    for symbol in all_symbols:
        print(symbol)
    print(len(all_symbols))
else:
    sys.exit(1)

# hardcoded pairs
minimal_interesting_symbols = ['ETHBTC', 'ETHUSDT', 'ETHUSDC', 'BTCUSDT', 'SOLUSDT']

current_prices = get_current_prices_with_timestamp(minimal_interesting_symbols)
if current_prices:
    print("Current prices for specified symbols:")
    for symbol, info in current_prices.items():
        print(f"{symbol}: {info['price']}")
else:
    sys.exit(1)