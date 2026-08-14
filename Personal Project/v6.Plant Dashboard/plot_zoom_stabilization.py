import pandas as pd
import matplotlib.pyplot as plt

# 1. Load your master plant log
df = pd.read_csv("full_master_plant_log.csv")

# 2. Create a focused 2-panel figure to inspect valve adjustments and temperature stabilization
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Subplot 1: Watching the gentle, gradual valve adjustments (Manipulated Variables)
ax1.plot(df["time_min"], df["u1_flow"], label="Unit 1 Utility Flow (kg/s) - Gradual Trim", color="dodgerblue", linewidth=1.5)
ax1.plot(df["time_min"], df["u2_flow"], label="Unit 2 Utility Flow (kg/s) - Gradual Trim", color="darkorange", linewidth=1.5)
ax1.set_title("Process Dynamics: Gradual, Critically-Damped Valve Adjustments (No Panic Slams)", fontsize=12, fontweight="bold")
ax1.set_ylabel("Utility Flow Rate (kg/s)")
ax1.legend(loc="upper right")
ax1.grid(True)

# Subplot 2: Watching how temperatures smoothly converge back to target without hunting
ax2.plot(df["time_min"], df["u2_outlet"], label="Unit 2 Outlet Temp (°C)", color="green", linewidth=2)
ax2.axhline(y=120.0, color="red", linestyle=":", label="Target Setpoint (120°C)")
ax2.set_title("Setpoint Convergence: Smooth Recovery Back to 120°C", fontsize=12, fontweight="bold")
ax2.set_xlabel("Simulation Time (Minutes)")
ax2.set_ylabel("Temperature (°C)")
ax2.legend(loc="upper right")
ax2.grid(True)

plt.tight_layout()

# 3. Save and show the stabilization graph
plt.savefig("stabilization_zoom_plot.png", dpi=300)
print("=== STABILIZATION ZOOM PLOT SAVED AS 'stabilization_zoom_plot.png' ===")
plt.show()