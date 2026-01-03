"""
Explainability Module
---------------------
This module explains WHY a traffic record was flagged as anomalous.

Approach:
- Learn baseline behavior from normal traffic
- Compare anomalous records against this baseline
- Generate human-readable reasons for deviation

This supports analyst trust and auditability.
"""

import pandas as pd

DATA_FILE = "data/processed/anomaly_results.csv"
OUTPUT_FILE = "data/processed/anomaly_explanations.csv"


def generate_explanations(df=None):
    """
    Generates explanations for anomalous traffic records.

    If a DataFrame is passed, it is used directly.
    Otherwise, anomaly_results.csv is loaded from disk.
    """

    # Load data if not provided
    if df is None:
        df = pd.read_csv(DATA_FILE)

    # Separate normal traffic to learn baseline behavior
    normal_df = df[df["anomaly_label"] == "Normal"]

    # Compute baseline statistics from normal traffic
    baseline = normal_df.mean(numeric_only=True)

    # Calculate request rate deviation from baseline
    df["req_rate_deviation"] = (
        (df["req_per_min"] / baseline["req_per_min"]).round(2)
    )

    def explain_row(row):
        """
        Generates explanation text for a single record
        by checking deviations across multiple features.
        """
        reasons = []

        if row["req_per_min"] > baseline["req_per_min"] * 2:
            reasons.append(
                f"Request rate exceeded baseline by {row['req_rate_deviation']}×"
            )

        if row["error_rate"] > baseline["error_rate"] * 2:
            reasons.append("Unusually high error rate observed")

        if row["avg_resp_time"] > baseline["avg_resp_time"] * 1.5:
            reasons.append("Response time significantly higher than baseline")

        if "avg_req_size" in row and row["avg_req_size"] > baseline.get("avg_req_size", 0) * 1.5:
            reasons.append("Abnormally large request payloads")

        if "unique_endpoints" in row and row["unique_endpoints"] > baseline.get("unique_endpoints", 0) * 1.5:
            reasons.append("Accessing unusually high number of endpoints")

        if not reasons:
            reasons.append("Multiple feature deviations from learned baseline")

        return "; ".join(reasons)

    # Apply explanations
    df["explanation"] = df.apply(
        lambda row: explain_row(row)
        if row["anomaly_label"] == "Anomaly"
        else "Traffic behavior within normal baseline",
        axis=1
    )

    # Save output for dashboard / debugging
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[INFO] Explainability generated → {OUTPUT_FILE}")

    return df


# Allow standalone execution
if __name__ == "__main__":
    generate_explanations()
