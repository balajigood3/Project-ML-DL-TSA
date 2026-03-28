import streamlit as st
import requests

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
        url = f"http://127.0.0.1:8000/analyze/{tag}"

        try:
            res = requests.get(url).json()

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

        except:
            st.error("⚠️ API not running. Start API first.")