import streamlit as st
import pandas as pd
import joblib

# --- BACKEND LOGIC (Previously FastAPI) ---
# This function mimics the "API" behavior internally
def get_analysis_data(tag):
    try:
        # If Error 13 persists, ensure EEAMB.csv is closed in Excel
        df = pd.read_csv("EEAMB.csv")
        model = joblib.load("eeamb_model.pkl")
        
        FEATURES = ["VR","VY","VB","IR","IY","IB","temperature","MW","MVAR","MVA"]
        
        data = df[df["tag"] == tag]
        
        if data.empty:
            row = df.sample(1).iloc[0]
        else:
            row = data.iloc[0]

        # Prediction Logic
        input_data = pd.DataFrame([row])[FEATURES]
        fault = model.predict(input_data)[0]
        load = row["load_percent"]

        return {
            "tag": tag,
            "equipment": row["equipment"],
            "fault": fault,
            "load": load,
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- FRONTEND LOGIC (Streamlit UI) ---
st.title("⚡ EEAMB - Electrical Equipment Analysis")

tag = st.text_input("Enter Tag Number (Ex: 1PM-700A)")

mode = st.selectbox(
    "Select Output Type",
    ["Condition","Fault","Full Output"]
)

if st.button("Analyze"):
    if tag == "":
        st.warning("Enter Tag Number")
    else:
        # Instead of requests.get, we call the function directly
        res = get_analysis_data(tag)
        
        if res["status"] == "success":
            st.subheader("🧾 Equipment Details")
            st.write("Tag:", res["tag"])
            st.write("Equipment:", res["equipment"])

            if mode == "Condition":
                st.write("Load:", res["load"], "%")
            
            elif mode == "Fault":
                st.write("Fault:", res["fault"])
                
            elif mode == "Full Output":
                st.subheader("🚨 Fault Analysis")
                st.write("Fault:", res["fault"])
                st.write("Load:", res["load"], "%")
                
                if res["load"] >= 120:
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
                st.write("Predictive + Corrective Required")
        else:
            # Fixed the error display syntax
            st.error(f"⚠️ Error: {res['message']}")
