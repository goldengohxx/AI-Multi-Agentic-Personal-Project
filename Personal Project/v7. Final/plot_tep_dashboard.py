import pandas as pd
import matplotlib.pyplot as plt

# 1. Load simulation log
df = pd.read_csv("tep_master_simulation_log.csv")

# 2. Create a professional 3-panel industrial engineering dashboard
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 14), sharex=True)

# Panel 1: Cascading Thermal Tracking & Inlet Disturbance
ax1.plot(df["time_min"], df["u1_outlet"], label="Unit 1 Outlet (°C)", color="dodgerblue", linestyle=":", linewidth=1.5)
ax1.plot(df["time_min"], df["u2_outlet"], label="Cascading Unit 2 Outlet (°C)", color="forestgreen", linewidth=2)
ax1.plot(df["time_min"], df["inlet_temp"], label="Inlet Feed Temp (°C) [Disturbance]", color="crimson", linestyle="-.", linewidth=1.2)
ax1.plot(df["time_min"], df["predicted_trend"], label="ML Forecaster Trend (°C)", color="darkorange", linestyle="--", linewidth=1.5)
ax1.axhline(y=120.0, color="red", linestyle=":", label="Target Setpoint (120°C)")
ax1.set_title("1. Hybrid AI Thermal Tracking & Feedforward Disturbance Rejection", fontsize=11, fontweight="bold")
ax1.set_ylabel("Temperature (°C)")
ax1.legend(loc="upper right", fontsize=8)
ax1.grid(True)

# Panel 2: Utility Flow & Autonomous Routing
ax2.plot(df["time_min"], df["u1_flow"], label="Unit 1 Utility Flow ($u_1$)", color="teal", linewidth=1.8)
ax2.plot(df["time_min"], df["u2_flow"], label="Unit 2 Utility Flow ($u_2$)", color="purple", linewidth=1.8)
ax2.set_title("2. Multi-Agent Utility Actuation & Autonomous Routing", fontsize=11, fontweight="bold")
ax2.set_ylabel("Flow Rate (kg/s)")
ax2.legend(loc="upper right", fontsize=8)
ax2.grid(True)

# Panel 3: Economic Audit (Traditional OPEX vs AI OPEX & Net Savings)
ax3.plot(df["time_min"], df["baseline_opex"], label="Traditional Baseline OPEX ($/min)", color="gray", linestyle="--", linewidth=1.5)
ax3.plot(df["time_min"], df["optimized_opex"], label="AI-Optimized OPEX ($/min)", color="blue", linewidth=1.5)
ax3.plot(df["time_min"], df["savings"], label="Cumulative Net Savings ($)", color="green", linewidth=2.5)
ax3.set_title("3. Economic Audit: Traditional OPEX vs. AI-Optimized OPEX & Cumulative Savings", fontsize=11, fontweight="bold")
ax3.set_xlabel("Simulation Time (Minutes)", fontsize=10)
ax3.set_ylabel("Cost ($/min) & Savings ($)", fontsize=10)
ax3.legend(loc="upper left", fontsize=8)
ax3.grid(True)

plt.tight_layout()

# 3. Save dashboard
plt.savefig("tep_predictive_dashboard.png", dpi=300)
print("=== 3-PANEL INDUSTRIAL AUDIT DASHBOARD SAVED AS 'tep_predictive_dashboard.png' ===")
plt.show()