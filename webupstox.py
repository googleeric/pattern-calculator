import requests

instrument_key = "NSE_EQ|INE002A01018"  # Corrected instrument key from /instruments
unit = "minutes"
interval = "5"
access_token = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIyVUJTTE4iLCJqdGkiOiI2ODFhM2ZmYWQ5NzY4ZjU5NDY2OTUyN2YiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc0NjU1MDc3OCwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzQ2NTY4ODAwfQ.AmxVY5ax-5-Be4QTY19VH_HXZ5nGXHNuDYDqF42Z2nE"  # Replace with actual token

url = f"https://api.upstox.com/v3/historical-candle/intraday/{instrument_key}/{unit}/{interval}"

headers = {
  'Accept': 'application/json',
  'Authorization': f'Bearer {access_token}'
}

response = requests.get(url, headers=headers)

print(response.json())  # Print the correct data or error message

