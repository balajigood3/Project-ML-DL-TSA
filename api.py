from fastapi import FastAPI, HTTPException
import pandas as pd
import joblib
import os

app = FastAPI()

# Get the directory where api.py is located to ensure paths are correct
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "eeamb_model.pkl")
CSV_PATH = os.path.join(BASE_DIR, "EEAMB.csv")

# Load resources with error handling
try:
    df = pd.read_csv(CSV_PATH)
    model = joblib.load(MODEL_PATH)
    print("Model and Data loaded successfully!")
except Exception as e:
    print(f"Error loading files: {e}")
    # Setting these to None so the app doesn't crash on startup 
    # but will provide an error when called
    model = None
    df = None

FEATURES = ["VR", "VY", "VB", "IR", "IY", "IB", "temperature", "MW", "MVAR", "MVA"]

def predict_fault(row):
    if model is None:
        # This prevents the 500 error and tells you the model is missing
        return "ERROR: Model not loaded. Re-train your model in Python 3.12."
    
    data = pd.DataFrame([row], columns=FEATURES)
    return model.predict(data)[0]

@app.get("/analyze/{tag}")
def analyze(tag: str):
    if df is None:
        raise HTTPException(status_code=500, detail="Data file not found on server")

    # Filter data by tag
    data = df[df["tag"] == tag]

    if data.empty:
        # If tag doesn't exist, pick a random sample for demonstration
        row = df.sample(1).iloc[0]
        actual_tag = row["tag"]
    else:
        row = data.iloc[0]
        actual_tag = tag

    try:
        fault = predict_fault(row)
        # Using .get() or checking keys is safer in case column names vary
        load = row.get("load_percent", "N/A")
        equipment = row.get("equipment", "Unknown")

        return {
            "requested_tag": tag,
            "matched_tag": actual_tag,
            "equipment": equipment,
            "fault": fault,
            "load": load
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
