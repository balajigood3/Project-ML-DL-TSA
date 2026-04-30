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
from pathlib import Path

# Page Configuration
st.set_page_config(page_title="EEAMB", layout="wide")

# =========================================
# DYNAMIC PATH SETTINGS (FIXES THE ERROR)
# =========================================
import pandas as pd
df = pd.read_csv('EEAMB.csv')
DATA_PATH = BASE_DIR / "EEAMB.csv"
MODEL_PATH = BASE_DIR / "eeamb_model.pk1"

# =========================================
# LOAD / TRAIN MODEL
# =========================================
@st.cache_resource
def load_or_train():
    # 1. Check if the CSV exists
    if not DATA_PATH.exists():
        st.error(f"❌ DATA FILE NOT FOUND! Ensure 'EEAMB.csv' is in the 'data' folder on GitHub.")
        st.stop()

    df = pd.read_csv(DATA_PATH)
    
    FEATURES = [
        "VR", "VY", "VB", 
        "IR", "IY", "IB", 
        "temperature", 
        "MW", "MVAR", "MVA"
    ]
    
    X = df[FEATURES]
    y = df["fault"]

    # 2. Try to load existing model, otherwise train a new one
    if MODEL_PATH.exists():
        model = joblib.load(MODEL_PATH)
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        model = RandomForestClassifier(n_estimators=100)
        model.fit(X_train, y_train)
        
        pred = model.predict(X_test)
        acc = accuracy_score(y_test, pred)
        
        # Save the model to the data folder
        joblib.dump(model, MODEL_PATH)
        st.success(f"✅ Model trained & saved to data folder | Accuracy: {round(acc,2)}")

    return model, df, FEATURES

# Run the loader
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
# UI SECTION
# =========================================
st.title("⚡ EEAMB - Electrical Equipment AI System")

col1, col2 = st.columns([1, 2])

with col1:
    tag = st.text_input("Enter Tag Number (Ex: 2PM-388A, 3PM-856B)")
    mode = st.selectbox(
        "Select Output Type", 
        ["Condition", "Fault", "Full Output"]
    )
    analyze_btn = st.button("Analyze System")

if analyze_btn:
    if not tag:
        st.warning("Please enter a Tag Number")
    else:
        # Search for the tag in the dataframe
        data = df[df["tag"].astype(str).str.contains(tag, case=False, na=False)]
        
        if data.empty:
            row = df.sample(1).iloc[0]
            st.warning(f"Tag '{tag}' not found → Showing Sample Prediction")
        else:
            row = data.iloc[0]

        # Extract values for prediction
        values = [
            row["VR"], row["VY"], row["VB"], 
            row["IR"], row["IY"], row["IB"], 
            row["temperature"], row["MW"], row["MVAR"], row["MVA"]
        ]
        
        fault = predict_fault(values)
        load = calculate_load(row["IR"], row["IY"], row["IB"])
        equipment = row.get("equipment", "Unknown Equipment")

        # Display Results
        st.divider()
        
        if mode == "Condition":
            st.metric("Load Percentage", f"{load}%")
            if load > 100:
                st.error("Overload Detected")
            else:
                st.success("Normal Load")

        elif mode == "Fault":
            st.subheader(f"Detected Fault: {fault}")

        elif mode == "Full Output":
            st.subheader("🧾 Equipment Overview")
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Tag:** {tag}")
            c2.write(f"**Type:** {equipment}")
            c3.write(f"**Load:** {load}%")

            st.subheader("🚨 Fault Analysis")
            if fault.lower() == "normal":
                st.success(f"Status: {fault}")
            else:
                st.error(f"Status: {fault}")

            st.subheader("🔧 Maintenance Advice")
            st.info(get_maintenance(equipment))
            
            with st.expander("Detailed Engineering Reason"):
                st.write(f"""
                The analysis indicates a **{fault}** state. 
                - Current Load: {load}%
                - Primary Action: {get_maintenance(equipment)}
                - Verify voltage levels (VR, VY, VB) for balance.
                """)
