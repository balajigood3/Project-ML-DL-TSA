import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

print("Libraries Loaded successfully")
# Load Dataset

df = pd.read_csv("EEAMB.csv")
df.info()
df.columns
# Features
X = df[[
    "VR","VY","VB",
    "IR","IY","IB",
    "temperature",
    "MW","MVAR","MVA"
]]
# Target

y = df["fault"]
# Train Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# Prediction
model = RandomForestClassifier()
model.fit(X_train, y_train)
pred = model.predict(X_test)
# Accuracy
acc = accuracy_score(y_test, pred)
print("Model Accuracy:", acc)
# Save Model
import joblib
joblib.dump(model, "eeamb_model.pk1")
print("Model Saved")
# Prediction Function
import joblib
model = joblib.load("eeamb_model.pk1")

def predict_fault(vr, vy, vb, ir, iy, ib, temp, mw, mvar, mva):
    data = [[vr, vy, vb, ir, iy, ib, temp, mw, mvar, mva]]
    prediction = model.predict(data)[0]
    return prediction
# Logic Engine
def calculate_load(ir, iy, ib, rated=100):
    avg = (ir+iy+ib)/3
    load = (avg/rated)*100
    return round(load, 2) 
# Knowledge Engine (Basic)
maintenance_knowledge = {
    "Motor": "Check bearings, lubrication, alignment",
    "Transformer": "Check oil, insulation, temperature",
    "Generator": "Check excitation, load balance" 
}

def get_maintenance(eq):
    return maintenance_knowledge.get(eq, "General inspection required")
# Final output function

def eeamb_output(eq, vr,vy,vb,ir,iy,ib,temp,mw,mvar,mva):
    fault = predict_fault(vr,vy,vb,ir,ib,iy,ib,temp,mw,mvar,mva)
    load = calculate_load(ir, iy, ib)
    maintenance = get_maintenance(eq)
    
    print("\n ========eeamb OUTPUT========")
    print("Equipment:", eq)
    print("Fault:", fault)
    print("Load %:", load)
    print("Maintenance:", maintenance)