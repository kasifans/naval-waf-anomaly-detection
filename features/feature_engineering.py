import pandas as pd
import os

# Ensure processed data directory exists
os.makedirs("data/processed", exist_ok=True)

RAW_FILE = "data/raw/traffic_logs.csv"
OUTPUT_FILE = "data/processed/features.csv"

# Load raw traffic logs
df = pd.read_csv(RAW_FILE)

# Convert timestamp to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Create 1-minute time window
df["time_window"] = df["timestamp"].dt.floor("T")

# Group by IP and time window
grouped = df.groupby(["ip", "time_window"])

# Feature engineering
features = grouped.agg(
    req_per_min=("ip", "count"),
    avg_resp_time=("resp_time", "mean"),
    error_rate=("status", lambda x: (x >= 400).mean()),
    avg_req_size=("req_size", "mean"),
    unique_endpoints=("endpoint", "nunique")
).reset_index()

# Burst score (simple normalization)
features["burst_score"] = features["req_per_min"] / features["req_per_min"].max()

# Drop helper columns
features = features.drop(columns=["time_window"])

# Save features
features.to_csv(OUTPUT_FILE, index=False)

print(f"[✓] Feature file created: {OUTPUT_FILE}")

