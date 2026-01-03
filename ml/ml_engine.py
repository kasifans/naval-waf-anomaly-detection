"""
ML Engine Orchestrator
=====================
This file connects all backend components into one clean pipeline.

Pipeline:
Features → Anomaly Detection → Explainability → Risk & Rules → Dashboard Output
"""

import os
import pandas as pd

from anomaly_detector import run_anomaly_detection
from explainability import generate_explanations

# ===================== PATHS =====================
FINAL_OUTPUT = "data/processed/rule_recommendations.csv"

os.makedirs("data/processed", exist_ok=True)


def compute_risk_score(df):
    """
    Combines multiple behavioral signals into a single risk score (0–10).
    """

    df["risk_score"] = (
        (df["req_per_min"] / df["req_per_min"].max()) * 4 +
        df["error_rate"] * 4 +
        (df["avg_resp_time"] / df["avg_resp_time"].max()) * 2
    ).round(2)

    return df


def assign_severity_and_action(df):
    """
    Converts risk score into severity levels and mitigation actions.
    """

    def severity(score):
        if score >= 7:
            return "High"
        elif score >= 4:
            return "Medium"
        return "Low"

    df["severity"] = df["risk_score"].apply(severity)

    def action(row):
        if row["severity"] == "High":
            return "Block IP and alert SOC immediately"
        elif row["severity"] == "Medium":
            return "Apply rate limiting and monitor closely"
        return "Allow traffic and continue monitoring"

    df["recommended_action"] = df.apply(action, axis=1)

    return df


def run_engine():
    print("[INFO] Starting ML engine pipeline")

    # Step 1: Anomaly detection
    df = run_anomaly_detection()

    # Step 2: Explainability
    df = generate_explanations(df)

    # Step 3: Risk scoring
    df = compute_risk_score(df)

    # Step 4: Severity + response rules
    df = assign_severity_and_action(df)

    # Step 5: Save final dataset for dashboard
    df.to_csv(FINAL_OUTPUT, index=False)

    print(f"[SUCCESS] ML pipeline completed → {FINAL_OUTPUT}")


if __name__ == "__main__":
    run_engine()
