import pandas as pd
import numpy as np
import os
from datetime import datetime

# Configuration
symbols = [
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
]
years = list(range(2000, 2025))

output_dir = "generated_test_data"
os.makedirs(output_dir, exist_ok=True)

# Initialize base prices for each symbol once, for continuity across years
base_prices = {symbol: np.random.uniform(50, 500) for symbol in symbols}

# Generate data for each year
for year in years:
    all_data = []  # Collect all data for the year

    # Loop through all 12 months
    for month in range(1, 13):
        for symbol in symbols:
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

                # Add record to the year's data
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

    # Create DataFrame and save to CSV for the entire year
    df = pd.DataFrame(all_data)
    output_file = f"{output_dir}/stock_data_Y{year}.csv"
    df.to_csv(output_file, index=False)
    print(f"Generated {len(df)} records in {output_file}")
