# =========================================
# ⚡ EEAMB STREAMLIT (NO API VERSION)
# FULL SINGLE FILE - PRO CLEAN
# =========================================

import streamlit as st
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os

st.set_page_config(page_title="EEAMB", layout="wide")

# =========================================
# LOAD / TRAIN MODEL
# =========================================
# Add the 'r' before the opening quote
MODEL_PATH = r"c:\Balaji-AI\MY PROJECTS\EEE\eeamb_model.pk1"
DATA_PATH = r"c:\Balaji-AI\MY PROJECTS\EEE\EEAMB.csv"

@st.cache_resource
def load_or_train():
    df = pd.read_csv(DATA_PATH)

    FEATURES = [
        "VR","VY","VB",
        "IR","IY","IB",
        "temperature",
        "MW","MVAR","MVA"
    ]

    X = df[FEATURES]
    y = df["fault"]

    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = RandomForestClassifier()
        model.fit(X_train, y_train)

        pred = model.predict(X_test)
        acc = accuracy_score(y_test, pred)

        joblib.dump(model, MODEL_PATH)
        st.success(f"Model trained & saved | Accuracy: {round(acc,2)}")

    return model, df, FEATURES


model, df, FEATURES = load_or_train()

# =========================================
# CORE FUNCTIONS
# =========================================

def predict_fault(values):
    data = pd.DataFrame([values], columns=FEATURES)
    return model.predict(data)[0]


def calculate_load(ir, iy, ib, rated=100):
    avg = (ir + iy + ib) / 3
    return round((avg / rated) * 100, 2)


maintenance_knowledge = {
    "Motor": "Check bearings, lubrication, alignment",
    "Transformer": "Check oil, insulation, temperature",
    "Generator": "Check excitation, load balance"
}

def get_maintenance(eq):
    return maintenance_knowledge.get(eq, "General inspection required")


# =========================================
# UI
# =========================================

st.title("⚡ EEAMB - Electrical Equipment AI System")

tag = st.text_input("Enter Tag Number (Ex: 2PM-388A, 3PM-856B)")

mode = st.selectbox(
    "Select Output Type",
    ["Condition", "Fault", "Full Output"]
)

if st.button("Analyze"):

    if tag == "":
        st.warning("Enter Tag Number")
    else:

        data = df[df["tag"] == tag]

        if data.empty:
            row = df.sample(1).iloc[0]
            st.warning("Tag not found → showing sample data")
        else:
            row = data.iloc[0]

        # Extract values
        values = [
            row["VR"], row["VY"], row["VB"],
            row["IR"], row["IY"], row["IB"],
            row["temperature"],
            row["MW"], row["MVAR"], row["MVA"]
        ]

        fault = predict_fault(values)
        load = calculate_load(row["IR"], row["IY"], row["IB"])
        equipment = row.get("equipment", "Unknown")

        st.subheader("🧾 Equipment Details")
        st.write("Tag:", tag)
        st.write("Equipment:", equipment)

        # ======================
        # MODES
        # ======================

        if mode == "Condition":
            st.write("Load:", load, "%")

        elif mode == "Fault":
            st.write("Fault:", fault)

        elif mode == "Full Output":

            st.subheader("🚨 Fault Analysis")
            st.write("Fault:", fault)
            st.write("Load:", load, "%")

            if load >= 120:
                st.error("🔴 CRITICAL CONDITION")
            else:
                st.success("🟢 NORMAL")

            st.subheader("🧠 Reason")
            st.write("""
Overload condition occurred due to current exceeding 120% of rated capacity

Possible Causes:
- Excess mechanical load
- Bearing failure
- Voltage imbalance
- Cooling failure
            """)

            st.subheader("🔧 Maintenance")
            st.write(get_maintenance(equipment))
