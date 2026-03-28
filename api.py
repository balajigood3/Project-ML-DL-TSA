from fastapi import FastAPI
import pandas as pd
import joblib

app = FastAPI()

df = pd.read_csv("EEAMB.csv")
model = joblib.load("eeamb_model.pkl")

FEATURES = [
    "VR","VY","VB",
    "IR","IY","IB",
    "temperature",
    "MW","MVAR","MVA"
]

def predict_fault(row):
    data = pd.DataFrame([row])[FEATURES]
    return model.predict(data)[0]

@app.get("/analyze/{tag}")
def analyze(tag: str):

    data = df[df["tag"] == tag]

    if data.empty:
        row = df.sample(1).iloc[0]
    else:
        row = data.iloc[0]

    fault = predict_fault(row)
    load = row["load_percent"]

    return {
        "tag": tag,
        "equipment": row["equipment"],
        "fault": fault,
        "load": load
    }