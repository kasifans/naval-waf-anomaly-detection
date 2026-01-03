"""
Anomaly Detector Module
----------------------
This module applies a trained Isolation Forest model to engineered
traffic features to detect anomalous behavior.

Key design rule:
- The feature names and order used at inference MUST exactly match
  those used during training. This file enforces that contract.
"""

import pandas as pd
import joblib
import os

# ===================== PATHS =====================
DATA_FILE = "data/processed/features.csv"
MODEL_FILE = "ml/models/isolation_forest.pkl"
OUTPUT_FILE = "data/processed/anomaly_results.csv"

# Ensure output directory exists
os.makedirs("data/processed", exist_ok=True)


def run_anomaly_detection(input_file=DATA_FILE):
    """
    Runs anomaly detection using a pre-trained Isolation Forest model.

    Steps:
    1. Load engineered feature data
    2. Load trained model
    3. Align inference features EXACTLY with training schema
    4. Predict anomaly scores and labels
    5. Save results for downstream processing
    """

    # -------------------------------
    # Load feature data
    # -------------------------------
    df = pd.read_csv(input_file)

    # -------------------------------
    # Load trained model
    # -------------------------------
    model = joblib.load(MODEL_FILE)

    # -------------------------------
    # 🔐 CRITICAL STEP:
    # Use model's own feature schema
    # -------------------------------
    if not hasattr(model, "feature_names_in_"):
        raise RuntimeError(
            "Model does not contain feature_names_in_. "
            "This usually means it was trained using a NumPy array "
            "instead of a DataFrame."
        )

    feature_columns = list(model.feature_names_in_)

    # Validate required columns exist
    missing = [col for col in feature_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required feature columns: {missing}")

    # Force correct feature order and names
    X = df[feature_columns].copy()

    # -------------------------------
    # Model inference
    # -------------------------------
    df["anomaly_score"] = model.decision_function(X)
    df["anomaly"] = model.predict(X)

    # Convert model output to readable labels
    df["anomaly_label"] = df["anomaly"].apply(
        lambda x: "Anomaly" if x == -1 else "Normal"
    )

    # -------------------------------
    # Save intermediate results
    # -------------------------------
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[✓] Anomaly detection complete → {OUTPUT_FILE}")

    return df


# =====================
# Standalone execution
# =====================
if __name__ == "__main__":
    run_anomaly_detection()