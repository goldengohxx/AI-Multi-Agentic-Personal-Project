import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the 24-hour stochastic simulation CSV log
df = pd.read_csv("stochastic_master_plant.csv")

# 2. Create subplots without using plt.figure()
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12), sharex=True)

# Subplot 1: Temperatures & Setpoint
ax1.plot(df["time_min"], df["inlet_temp"], label="Inlet Temp ($^\\circ\\text{C}$)", color="blue", linestyle="--")
ax1.plot(df["time_min"], df["u1_outlet"], label="Unit 1 Outlet ($^\\circ\\text{C}$)", color="orange")
ax1.plot(df["time_min"], df["u2_outlet"], label="Unit 2 Outlet (Target $120^\\circ\\text{C}$)", color="green", linewidth=2)
ax1.axhline(y=120.0, color="red", linestyle=":", label="Target Setpoint ($120^\\circ\\text{C}$)")
ax1.set_title("24-Hour Stochastic Master Plant Simulation: Thermal Performance", fontsize=12, fontweight="bold")
ax1.set_ylabel("Temperature ($^\\circ\\text{C}$)")
ax1.legend(loc="upper right")
ax1.grid(True)

# Subplot 2: Utility Flows
ax2.plot(df["time_min"], df["u1_flow"], label="Unit 1 Utility Flow (kg/s)", color="dodgerblue")
ax2.plot(df["time_min"], df["u2_flow"], label="Unit 2 Utility Flow (kg/s)", color="darkorange")
ax2.set_title("Manipulated Variables: Utility Flows & Autonomous Rerouting", fontsize=12, fontweight="bold")
ax2.set_ylabel("Flow Rate (kg/s)")
ax2.legend(loc="upper right")
ax2.grid(True)

# Highlight active fouling fault periods across all subplots
fault_df = df[df["status"].str.contains("FOULING")]
if not fault_df.empty:
    # Find contiguous fault blocks or shade overall intervals
    min_fault = fault_df["time_min"].min()
    max_fault = fault_df["time_min"].max()
    for ax in [ax1, ax2, ax3]:
        ax.axvspan(min_fault, max_fault, color="red", alpha=0.15, label="U1 Fouling Fault Active")

# Subplot 3: Economic OPEX & Carbon Tax
ax3.plot(df["time_min"], df["opex"], label="Total Hourly OPEX ($/hr)", color="purple")
ax3.set_title("Dynamic Economic Audit: Hourly OPEX & Carbon Tax Load", fontsize=12, fontweight="bold")
ax3.set_xlabel("Simulation Time (Minutes)")
ax3.set_ylabel("OPEX ($/hr)")
ax3.legend(loc="upper right")
ax3.grid(True)

plt.tight_layout()

# 3. Save the plot using savefig() without show()
plt.savefig("stochastic_plant_performance.png", dpi=300)
print("=== PLOT SUCCESSFULLY GENERATED AND SAVED AS 'stochastic_plant_performance.png' ===")