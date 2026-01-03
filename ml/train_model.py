import pandas as pd
import os
import joblib
from sklearn.ensemble import IsolationForest

# Paths
DATA_FILE = "data/processed/features.csv"

MODEL_DIR = "ml/models"
MODEL_FILE = os.path.join(MODEL_DIR, "isolation_forest.pkl")

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# Load feature data
df = pd.read_csv(DATA_FILE)

# Drop non-feature columns
X = df.drop(columns=["ip"])

# Train Isolation Forest
model = IsolationForest(
    n_estimators=100,
    contamination=0.15,
    random_state=42
)

model.fit(X)

# Save trained model
joblib.dump(model, MODEL_FILE)

print(f"[✓] Model trained and saved at: {MODEL_FILE}")
