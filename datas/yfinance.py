import yfinance as yf
import os

# === Parameters ===
ticker = "STM.MI"   # for NYSE. Use "STM.MI" if you want Milan exchange
start_date = "2024-09-25"
end_date = "2025-09-24"
output_dir = "mhsizzles/backtrader/datas/"
output_file = os.path.join(output_dir, f"{ticker}.csv")

# === Create directory if it doesn't exist ===
os.makedirs(output_dir, exist_ok=True)

# === Download data ===
data = yf.download(ticker, start=start_date, end=end_date)

# === Save to CSV ===
data.to_csv(output_file)

print(f"Saved {ticker} data to {output_file}")
