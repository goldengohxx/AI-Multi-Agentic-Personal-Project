import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the new master log
df = pd.read_csv("full_master_plant_log.csv")

# 2. Create the 4-panel dashboard figure
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 14), sharex=True)

# Panel 1: Coupled Temperatures
ax1.plot(df["time_min"], df["inlet_temp"], label="Inlet Feed Temp (°C)", color="blue", linestyle="--")
ax1.plot(df["time_min"], df["u1_outlet"], label="Unit 1 Outlet (~100°C)", color="orange")
ax1.plot(df["time_min"], df["u2_outlet"], label="Unit 2 Outlet (Target 120°C)", color="green", linewidth=2)
ax1.axhline(y=120.0, color="red", linestyle=":", label="Target Setpoint (120°C)")
ax1.set_title("1. Coupled Process Thermodynamics: Temperature Cascade & Disturbance Tracking", fontsize=11, fontweight="bold")
ax1.set_ylabel("Temperature (°C)")
ax1.legend(loc="upper right")
ax1.grid(True)

# Panel 2: Utility Flows
ax2.plot(df["time_min"], df["u1_flow"], label="Unit 1 Utility Flow (kg/s)", color="dodgerblue")
ax2.plot(df["time_min"], df["u2_flow"], label="Unit 2 Utility Flow (kg/s)", color="darkorange")
ax2.set_title("2. Manipulated Variables: AI Valve Adjustments & Rerouting", fontsize=11, fontweight="bold")
ax2.set_ylabel("Flow Rate (kg/s)")
ax2.legend(loc="upper right")
ax2.grid(True)

# Panel 3: Economic Audit (Baseline vs AI OPEX)
ax3.plot(df["time_min"], df["baseline_opex"], label="Baseline OPEX (Unmanaged Plant) ($/hr)", color="red", linestyle="--")
ax3.plot(df["time_min"], df["optimized_opex"], label="AI-Optimized OPEX ($/hr)", color="purple", linewidth=2)
ax3.set_title("3. Economic Audit: Traditional Cost vs. AI-Optimized Cost", fontsize=11, fontweight="bold")
ax3.set_ylabel("Cost ($/hr)")
ax3.legend(loc="upper right")
ax3.grid(True)

# Panel 4: Cumulative Net Savings
df["cumulative_savings"] = df["savings"].cumsum() / 60.0
ax4.plot(df["time_min"], df["cumulative_savings"], label="Cumulative Net Currency Saved ($)", color="forestgreen", linewidth=2)
ax4.set_title("4. Financial Impact: Total Net Savings Generated Over Time", fontsize=11, fontweight="bold")
ax4.set_xlabel("Simulation Time (Minutes)")
ax4.set_ylabel("Savings ($)")
ax4.legend(loc="upper right")
ax4.grid(True)

plt.tight_layout()

# Save the dashboard image
plt.savefig("full_plant_comparison_dashboard.png", dpi=300)
print("=== COMPREHENSIVE DASHBOARD SUCCESSFULLY GENERATED & SAVED AS 'full_plant_comparison_dashboard.png' ===")
plt.show()