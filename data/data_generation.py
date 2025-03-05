import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

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
years = [
    2020,
    2021,
    2022,
    2023,
    2024,
    2025,
]
records_per_symbol_per_month = 21  # Trading days per month approx

output_dir = "generated_test_data"
os.makedirs(output_dir, exist_ok=True)

# Generate data for each year/quarter
for year in years:
    for quarter in range(1, 5):
        start_month = (quarter - 1) * 3 + 1
        end_month = quarter * 3

        all_data = []

        for month in range(start_month, end_month + 1):
            for symbol in symbols:
                # Create a base price and volume for each symbol
                base_price = np.random.uniform(50, 500)
                base_volume = np.random.randint(1000000, 20000000)

                # Generate daily data for the month
                for day in range(1, records_per_symbol_per_month + 1):
                    # Make sure we don't generate invalid dates
                    try:
                        date = datetime(year, month, day).strftime("%Y-%m-%d")
                    except ValueError:
                        continue

                    # Generate price movement
                    price_change = np.random.normal(0, 0.02)  # 2% std dev

                    # Calculate OHLC prices
                    open_price = base_price * (1 + np.random.normal(0, 0.01))
                    high_price = open_price * (1 + abs(np.random.normal(0, 0.015)))
                    low_price = open_price * (1 - abs(np.random.normal(0, 0.015)))
                    close_price = open_price * (1 + price_change)

                    # Update base price for next day
                    base_price = close_price

                    # Generate volume with some randomness
                    volume = int(base_volume * np.random.uniform(0.5, 1.5))

                    # Add record
                    all_data.append(
                        {
                            "date": date,
                            "symbol": symbol,
                            "open": round(open_price, 2),
                            "high": round(high_price, 2),
                            "low": round(low_price, 2),
                            "close": round(close_price, 2),
                            "volume": volume,
                        }
                    )

        # Create DataFrame and save to CSV
        # One CSV file per year and quarter
        df = pd.DataFrame(all_data)
        output_file = f"{output_dir}/stock_data_Y{year}_Q{quarter}.csv"
        df.to_csv(output_file, index=False)
        print(f"Generated {len(df)} records in {output_file}")
