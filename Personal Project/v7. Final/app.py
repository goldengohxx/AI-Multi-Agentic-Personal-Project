import streamlit as st
import pandas as pd
import numpy as np
import time
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# 1. Page Configuration
st.set_page_config(page_title="TEP Fast-Forward Plant Digital Twin", layout="wide")
st.title("🏭 Autonomous Multi-Agent Fast-Forward SCADA Dashboard")
st.markdown("*Industrial Digital Twin: Accelerate 24-hour plant operations in seconds with live operator intervention.*")

# 2. Initialize Machine Learning Forecaster
@st.cache_resource
def load_forecaster():
    try:
        df = pd.read_excel("mode1_normal_500.xlsx")
        target_col = df.columns[8] if len(df.columns) > 8 else df.columns[-1]
        feature_cols = [df.columns[1], df.columns[2], df.columns[3]]
        clean_df = df[feature_cols + [target_col]].dropna()
        X = clean_df[feature_cols]
        y = clean_df[target_col]
        
        model = RandomForestRegressor(n_estimators=30, random_state=42)
        model.fit(X, y)
        return model, feature_cols, X.mean(), y.mean(), y.std()
    except Exception as e:
        return None, None, None, None, None

model, feature_cols, f_means, t_mean, t_std = load_forecaster()

# 3. Initialize Session State
def reset_simulation():
    st.session_state.history = []
    st.session_state.time_min = 0.0
    st.session_state.inlet_temp = 25.0
    st.session_state.u1_flow = 8.0
    st.session_state.u1_outlet = 100.0
    st.session_state.u2_flow = 5.0
    st.session_state.u2_outlet = 120.0
    st.session_state.base_u1 = 10.0
    st.session_state.base_u2 = 6.0
    st.session_state.base_u1_out = 100.0
    st.session_state.base_u2_out = 120.0
    st.session_state.cumulative_savings = 0.0
    st.session_state.is_running = False
    st.session_state.unit1_fault = False

if "history" not in st.session_state:
    reset_simulation()

# 4. Operator Control Room Sidebar
st.sidebar.header("🎛️ Operator Control Room")
st.sidebar.markdown("Control simulation speed, inject ambient shocks, and toggle Unit 1 faults.")

# Execution Buttons
col_b1, col_b2, col_b3 = st.sidebar.columns(3)
if col_b1.button("▶️ Start Fast"):
    st.session_state.is_running = True
if col_b2.button("⏹️ Pause"):
    st.session_state.is_running = False
if col_b3.button("🔄 Reset"):
    reset_simulation()
    st.rerun()

st.sidebar.markdown("---")
# Speed Multiplier Slider
sim_speed = st.sidebar.slider("⚡ Simulation Speed (Minutes per Tick)", min_value=1, max_value=30, value=5, step=1)

# Equipment Fault Button Controls
st.sidebar.markdown("### 🛠️ Unit 1 Equipment Status")
col_f1, col_f2 = st.sidebar.columns(2)
if col_f1.button("⚠️ Break Unit 1"):
    st.session_state.unit1_fault = True
if col_f2.button("✅ Fix Unit 1"):
    st.session_state.unit1_fault = False

status_color = "🔴 FAULT ACTIVE (Fouling)" if st.session_state.unit1_fault else "🟢 NORMAL OPERATION"
st.sidebar.markdown(f"**Current Status:** {status_color}")

inject_shock = st.sidebar.slider("🌡️ Inlet Ambient Disturbance (°C)", min_value=0.0, max_value=8.0, value=0.0, step=0.5)

# 5. Core Simulation Step Function (Multi-step batching for fast-forward)
def step_simulation(steps=1):
    for _ in range(steps):
        st.session_state.time_min += 1.0
        dt = 1.0
        
        target_inlet = 25.0 + inject_shock
        st.session_state.inlet_temp += (target_inlet - st.session_state.inlet_temp) * 0.1
        
        eff = 0.35 if st.session_state.unit1_fault else 1.2
        base_eff = 0.35 if st.session_state.unit1_fault else 1.0
        water_cp, water_inlet = 4.184, 180.0
        crude_mass, crude_cp = 2.78, 2.3
        alpha = dt / (5.0 + dt)
        
        # AI Supervisor Control Actions
        u1_error = 100.0 - st.session_state.u1_outlet
        u2_error = 120.0 - st.session_state.u2_outlet
        
        if st.session_state.unit1_fault:
            a1, a2 = -0.2, 0.2
        else:
            a1 = 0.03 * u1_error
            a2 = 0.05 * u2_error
            
        # Cascading Plant Step
        st.session_state.u1_flow = max(1.0, min(st.session_state.u1_flow + a1, 15.0))
        q1 = st.session_state.u1_flow * water_cp * (water_inlet - st.session_state.inlet_temp) * 0.08 * eff
        st.session_state.u1_outlet += alpha * ((st.session_state.inlet_temp + (q1 / (crude_mass * crude_cp))) - st.session_state.u1_outlet)
        
        st.session_state.u2_flow = max(1.0, min(st.session_state.u2_flow + a2, 15.0))
        q2 = st.session_state.u2_flow * water_cp * (water_inlet - st.session_state.u1_outlet) * 0.06 * 1.0
        st.session_state.u2_outlet += alpha * ((st.session_state.u1_outlet + (q2 / (crude_mass * crude_cp))) - st.session_state.u2_outlet)
        
        # ML Trend Prediction
        pred_trend = 120.0
        if model is not None:
            scaled_u1 = st.session_state.u1_flow + f_means.iloc[0] - 10.0
            scaled_u2 = st.session_state.u2_flow + f_means.iloc[1] - 5.0
            scaled_in = st.session_state.inlet_temp + f_means.iloc[2] - 25.0
            inp = pd.DataFrame([[scaled_u1, scaled_u2, scaled_in]], columns=feature_cols)
            raw_pred = float(model.predict(inp)[0])
            norm_pred = (raw_pred - t_mean) / t_std
            pred_trend = 120.0 + (norm_pred * 2.0)
            
        # Economics Audit
        tax = 40.0
        ai_gj = (q1 + q2) * 3.6
        ai_co2 = (ai_gj * 50.0) / 1000.0
        opt_opex = (ai_co2 * tax) + ((st.session_state.u1_flow + st.session_state.u2_flow) * 15.0)
        
        base_q1 = st.session_state.base_u1 * water_cp * (water_inlet - st.session_state.inlet_temp) * 0.08 * base_eff
        st.session_state.base_u1_out += alpha * ((st.session_state.inlet_temp + (base_q1 / (crude_mass * crude_cp))) - st.session_state.base_u1_out)
        base_q2 = st.session_state.base_u2 * water_cp * (water_inlet - st.session_state.base_u1_out) * 0.06 * base_eff
        st.session_state.base_u2_out += alpha * ((st.session_state.base_u1_out + (base_q2 / (crude_mass * crude_cp))) - st.session_state.base_u2_out)
        
        base_gj = (base_q1 + base_q2) * 3.6
        base_co2 = (base_gj * 50.0) / 1000.0
        base_opex = (base_co2 * tax) + ((st.session_state.base_u1 + st.session_state.base_u2) * 15.0)
        
        marginal_savings = base_opex - opt_opex
        st.session_state.cumulative_savings += marginal_savings
        
        st.session_state.history.append({
            "time_min": st.session_state.time_min,
            "inlet_temp": round(st.session_state.inlet_temp, 2),
            "u1_outlet": round(st.session_state.u1_outlet, 2),
            "u2_outlet": round(st.session_state.u2_outlet, 2),
            "predicted_trend": round(pred_trend, 2),
            "u1_flow": round(st.session_state.u1_flow, 2),
            "u2_flow": round(st.session_state.u2_flow, 2),
            "savings": round(st.session_state.cumulative_savings, 2)
        })

# 6. Continuous Fast-Forward Execution Loop
if st.session_state.is_running:
    step_simulation(steps=sim_speed) # Fast-forward multiple minutes per tick!
    time.sleep(0.08)
    st.rerun()

# 7. Render Dashboards
if len(st.session_state.history) > 0:
    df_history = pd.DataFrame(st.session_state.history)
    
    st.subheader("📈 Real-Time Fast-Forward Panel 1: Cascading Thermal Tracking")
    st.line_chart(df_history.set_index("time_min")[["u1_outlet", "u2_outlet", "inlet_temp", "predicted_trend"]])
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.subheader("⚙️ Panel 2: Utility Actuation")
        st.line_chart(df_history.set_index("time_min")[["u1_flow", "u2_flow"]])
    with col_l2:
        st.subheader("💰 Panel 3: Cumulative Net Savings ($)")
        st.line_chart(df_history.set_index("time_min")[["savings"]])
else:
    st.info("👈 Click **'▶️ Start Fast'** in the sidebar to launch the high-speed digital twin!")