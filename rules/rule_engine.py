import pandas as pd
import os

INPUT_FILE = "data/processed/anomaly_explanations.csv"
OUTPUT_FILE = "data/processed/rule_recommendations.csv"

os.makedirs("data/processed", exist_ok=True)

# Load data
df = pd.read_csv(INPUT_FILE)

# ------------------ RISK SCORING ------------------

def calculate_risk(row):
    score = 0

    # Request rate impact (max 30)
    score += min(row["req_per_min"] * 0.5, 30)

    # Error rate impact (max 40)
    score += row["error_rate"] * 40

    # Burst behavior impact (max 30)
    score += row["burst_score"] * 30

    return int(min(score, 100))


df["risk_score"] = df.apply(calculate_risk, axis=1)


def assign_severity(score):
    if score >= 70:
        return "High"
    elif score >= 40:
        return "Medium"
    else:
        return "Low"


df["severity"] = df["risk_score"].apply(assign_severity)


def recommend_rule(row):
    if row["anomaly_label"] != "Anomaly":
        return "No action required"

    explanation = row["explanation"].lower()

    if "high request rate" in explanation:
        return "Rate limit IP for 5 minutes"

    if "error rate" in explanation:
        return "Temporarily block IP"

    if "payload" in explanation:
        return "Inspect payload and block if repeated"

    return "Monitor traffic closely"

# Generate rule recommendations
df["recommended_action"] = df.apply(recommend_rule, axis=1)

# Save rules
df.to_csv(OUTPUT_FILE, index=False)

print(f"[✓] Rule recommendations created: {OUTPUT_FILE}")
