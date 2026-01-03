import csv
import random
from datetime import datetime, timedelta
import os

# Ensure data directory exists
os.makedirs("data/raw", exist_ok=True)

OUTPUT_FILE = "data/raw/traffic_logs.csv"

IPS = [f"10.0.0.{i}" for i in range(1, 50)]
ENDPOINTS = ["/", "/login", "/api/data", "/api/login", "/admin"]
METHODS = ["GET", "POST"]
USER_AGENTS = ["Mozilla/5.0", "Chrome/120.0", "Safari/15.0", "bot-agent"]

# ---------------- NORMAL TRAFFIC ----------------
def generate_normal_request(timestamp):
    return {
        "timestamp": timestamp,
        "ip": random.choice(IPS),
        "endpoint": random.choice(ENDPOINTS[:-1]),
        "method": random.choice(METHODS),
        "status": random.choice([200, 200, 200, 404]),
        "req_size": random.randint(200, 800),
        "resp_time": random.randint(80, 250),
        "user_agent": random.choice(USER_AGENTS[:-1])
    }

# ---------------- BURST ATTACK ----------------
def generate_attack_request(timestamp):
    return {
        "timestamp": timestamp,
        "ip": random.choice(["10.0.0.99", "10.0.0.100"]),
        "endpoint": random.choice(["/login", "/api/login", "/admin"]),
        "method": "POST",
        "status": random.choice([401, 403, 500]),
        "req_size": random.randint(900, 2000),
        "resp_time": random.randint(300, 800),
        "user_agent": "bot-agent"
    }

# ---------------- STEALTH ATTACK (LOW & SLOW) ----------------
def generate_stealth_attack(timestamp):
    return {
        "timestamp": timestamp,
        "ip": "10.0.0.200",              # same IP always
        "endpoint": "/api/login",        # sensitive endpoint
        "method": "POST",
        "status": random.choice([401, 403]),
        "req_size": random.randint(650, 850),
        "resp_time": random.randint(220, 350),
        "user_agent": "Mozilla/5.0"      # looks human
    }

# ---------------- MAIN TRAFFIC GENERATION ----------------
def generate_traffic(minutes=15):
    start_time = datetime.now()
    rows = []

    for minute in range(minutes):
        current_time = start_time + timedelta(minutes=minute)

        # Normal traffic
        for _ in range(random.randint(30, 60)):
            rows.append(generate_normal_request(current_time))

        # Burst attack (obvious)
        if minute % 4 == 0:
            for _ in range(random.randint(20, 40)):
                rows.append(generate_attack_request(current_time))

        # Stealth attack (low & slow, hard to detect)
        if minute >= 6:
            rows.append(generate_stealth_attack(current_time))

    return rows

# ---------------- SAVE TO CSV ----------------
def save_to_csv(rows):
    with open(OUTPUT_FILE, "w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp",
                "ip",
                "endpoint",
                "method",
                "status",
                "req_size",
                "resp_time",
                "user_agent"
            ]
        )
        writer.writeheader()
        writer.writerows(rows)

# ---------------- RUN ----------------
if __name__ == "__main__":
    traffic_data = generate_traffic(minutes=15)
    save_to_csv(traffic_data)
    print(f"[✓] Traffic data generated: {OUTPUT_FILE}")
