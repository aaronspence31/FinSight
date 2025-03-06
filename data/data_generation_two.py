import pandas as pd
import numpy as np
import os
from datetime import datetime
import string
import random

# Configuration - Significantly increase the number of symbols
# Start with the original symbols
base_symbols = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "META",
    "TSLA",
    "NVDA",
    "PYPL",
    "NFLX",
    "INTC",
    "AMD",
    "CSCO",
    "ORCL",
    "IBM",
    "ADBE",
    "CRM",
    "QCOM",
    "TXN",
    "AVGO",
    "MU",
    "JPM",
    "BAC",
    "WMT",
    "DIS",
    "SBUX",
    "KO",
    "PEP",
    "JNJ",
    "PFE",
    "MRK",
    "V",
    "MA",
    "HD",
    "XOM",
    "CVX",
    "GE",
    "BA",
    "CMCSA",
    "T",
    "VZ",
    "NKE",
    "MCD",
    "UNH",
    "PG",
    "GS",
]


# Generate additional synthetic symbols to increase dataset size
def generate_random_symbol(length=4):
    return "".join(random.choices(string.ascii_uppercase, k=length))


# Generate 10000 additional symbols
additional_symbols = []
while len(additional_symbols) < 10000:
    new_symbol = generate_random_symbol()
    if new_symbol not in base_symbols and new_symbol not in additional_symbols:
        additional_symbols.append(new_symbol)

symbols = base_symbols + additional_symbols
print(f"Total number of symbols to generate data for: {len(symbols)}")

# Reduce the year range to keep generation time reasonable while still having large files
years = list(range(2005, 2010))

output_dir = "generated_test_data_two"
os.makedirs(output_dir, exist_ok=True)

# Initialize base prices for each symbol once, for continuity across years
base_prices = {symbol: np.random.uniform(50, 500) for symbol in symbols}

print("Starting data generation - this may take a while for large datasets...")

# Generate data for each year and month, consolidating all symbols into one file per month
for year in years:
    for month in range(1, 13):
        month_name = datetime(year, month, 1).strftime("%b")
        print(f"Generating data for {month_name} {year}...")

        # Collect data for all symbols for this month
        all_data = []

        # Track progress
        symbol_count = 0
        total_symbols = len(symbols)

        for symbol in symbols:
            symbol_count += 1
            if symbol_count % 200 == 0:
                print(f"  Processing symbol {symbol_count}/{total_symbols}...")

            # Set base volume per symbol per month
            base_volume = np.random.randint(1000000, 20000000)

            # Loop through all possible days in the month
            for day in range(1, 32):
                try:
                    date = datetime(year, month, day)
                    # Skip weekends (Saturday=5, Sunday=6)
                    if date.weekday() >= 5:
                        continue
                    date_str = date.strftime("%Y-%m-%d")
                except ValueError:
                    continue  # Skip invalid dates (e.g., Feb 30)

                # Generate price movement using the current base price
                price_change = np.random.normal(0, 0.02)  # 2% std dev
                open_price = base_prices[symbol] * (1 + np.random.normal(0, 0.01))
                high_price = open_price * (1 + abs(np.random.normal(0, 0.015)))
                low_price = open_price * (1 - abs(np.random.normal(0, 0.015)))
                close_price = open_price * (1 + price_change)

                # Update base price for the next trading day
                base_prices[symbol] = close_price

                # Generate volume with randomness
                volume = int(base_volume * np.random.uniform(0.5, 1.5))

                # Add record to the consolidated data for this month
                all_data.append(
                    {
                        "date": date_str,
                        "symbol": symbol,
                        "open": round(open_price, 2),
                        "high": round(high_price, 2),
                        "low": round(low_price, 2),
                        "close": round(close_price, 2),
                        "volume": volume,
                    }
                )

        # Create DataFrame and save to CSV for this month (all symbols)
        if all_data:  # Only create file if there's data
            df = pd.DataFrame(all_data)

            # Create a descriptive filename with year and month information
            output_file = (
                f"{output_dir}/stock_data_Y{year}_M{month:02d}_{month_name}.csv"
            )

            # Save to CSV with optimized settings for large files
            print(f"  Saving {len(df)} records to {output_file}...")
            df.to_csv(output_file, index=False, chunksize=100000)

            # Add some statistics about the file
            symbol_count = df["symbol"].nunique()
            date_count = df["date"].nunique()
            file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(
                f"  - File contains data for {symbol_count} symbols across {date_count} trading days"
            )
            print(f"  - File size: {file_size_mb:.2f} MB")

            # If file is very large, provide additional information
            if file_size_mb > 100:
                print(
                    f"  - Large file detected! Consider using this for partition testing"
                )

print("Data generation complete!")
print(f"Generated files are in the '{output_dir}' directory")
