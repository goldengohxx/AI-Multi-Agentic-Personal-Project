import random
import csv
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

class TEPMachineLearningForecaster:
    def __init__(self, excel_filepath):
        print(f"Initializing ML Forecaster using '{excel_filepath}'...")
        try:
            df = pd.read_excel(excel_filepath)
            target_col = df.columns[8] if len(df.columns) > 8 else df.columns[-1]
            self.feature_cols = [df.columns[1], df.columns[2], df.columns[3]]
            
            clean_df = df[self.feature_cols + [target_col]].dropna()
            X = clean_df[self.feature_cols]
            y = clean_df[target_col]
            
            self.feature_means = X.mean()
            self.target_mean = y.mean()
            self.target_std = y.std() if y.std() != 0 else 1.0
            
            self.model = RandomForestRegressor(n_estimators=50, random_state=42)
            self.model.fit(X, y)
            self.is_trained = True
            print("TEP Machine Learning Model successfully integrated into control loop!")
        except Exception as e:
            print(f"Warning: Could not load TEP file ({e}). Using fallback calculation.")
            self.is_trained = False

    def predict_next_state(self, u1_val, u2_val, inlet_val):
        if not self.is_trained:
            return 120.0
        scaled_u1 = u1_val + self.feature_means.iloc[0] - 10.0
        scaled_u2 = u2_val + self.feature_means.iloc[1] - 5.0
        scaled_inlet = inlet_val + self.feature_means.iloc[2] - 25.0
        
        prediction_input = pd.DataFrame([[scaled_u1, scaled_u2, scaled_inlet]], columns=self.feature_cols)
        raw_pred = float(self.model.predict(prediction_input)[0])
        
        normalized_pred = (raw_pred - self.target_mean) / self.target_std
        return 120.0 + (normalized_pred * 2.0)
    
class FullPlantTEPSimulator:
    def __init__(self, ml_forecaster):
        self.time_min = 0.0
        self.forecaster = ml_forecaster
        
        self.inlet_temp = 25.0
        self.u1_flow = 8.0
        self.u1_outlet = 100.0
        self.u2_flow = 5.0
        self.u2_outlet = 120.0
        
        self.base_u1_flow = 10.0
        self.base_u2_flow = 6.0
        self.base_u1_outlet = 100.0
        self.base_u2_outlet = 120.0
        
        self.carbon_tax_rate = 40.0
        self.utility_unit_cost = 15.0
        self.total_cumulative_savings = 0.0

    def step(self, action_u1, action_u2, fault_active=False, dt_min=1.0, active_disturbance=0.0):
        self.time_min += dt_min
        
        cycle_time = self.time_min % 1440
        self.carbon_tax_rate = 40.0 + 25.0 * (1.0 if 240 <= cycle_time <= 720 else 0.0)
        
        target_inlet = 25.0 + active_disturbance
        self.inlet_temp += (target_inlet - self.inlet_temp) * 0.1
        
        eff = 0.35 if fault_active else 1.2
        base_eff = 0.35 if fault_active else 1.0
        
        water_cp, water_inlet = 4.184, 180.0
        crude_mass, crude_cp = 2.78, 2.3
        alpha = dt_min / (5.0 + dt_min)
        
        # AI-Optimized Plant
        self.u1_flow += action_u1
        self.u1_flow = max(1.0, min(self.u1_flow, 15.0))
        q1 = self.u1_flow * water_cp * (water_inlet - self.inlet_temp) * 0.08 * eff
        self.u1_outlet += alpha * ((self.inlet_temp + (q1 / (crude_mass * crude_cp))) - self.u1_outlet)
        
        self.u2_flow += action_u2
        self.u2_flow = max(1.0, min(self.u2_flow, 15.0))
        q2 = self.u2_flow * water_cp * (water_inlet - self.u1_outlet) * 0.06 * 1.0
        self.u2_outlet += alpha * ((self.u1_outlet + (q2 / (crude_mass * crude_cp))) - self.u2_outlet)
        
        predicted_trend = self.forecaster.predict_next_state(self.u1_flow, self.u2_flow, self.inlet_temp)
        
        ai_gj = (q1 + q2) * 3.6
        ai_co2 = (ai_gj * 50.0) / 1000.0
        optimized_opex = (ai_co2 * self.carbon_tax_rate) + ((self.u1_flow + self.u2_flow) * self.utility_unit_cost)
        
        # Baseline Unoptimized Plant
        base_q1 = self.base_u1_flow * water_cp * (water_inlet - self.inlet_temp) * 0.08 * base_eff
        self.base_u1_outlet += alpha * ((self.inlet_temp + (base_q1 / (crude_mass * crude_cp))) - self.base_u1_outlet)
        
        base_q2 = self.base_u2_flow * water_cp * (water_inlet - self.base_u1_outlet) * 0.06 * base_eff
        self.base_u2_outlet += alpha * ((self.base_u1_outlet + (base_q2 / (crude_mass * crude_cp))) - self.base_u2_outlet)
        
        base_gj = (base_q1 + base_q2) * 3.6
        base_co2 = (base_gj * 50.0) / 1000.0
        baseline_opex = (base_co2 * self.carbon_tax_rate) + ((self.base_u1_flow + self.base_u2_flow) * self.utility_unit_cost)
        
        marginal_savings = baseline_opex - optimized_opex
        self.total_cumulative_savings += marginal_savings
        
        return {
            "time_min": round(self.time_min, 1),
            "carbon_tax": round(self.carbon_tax_rate, 1),
            "inlet_temp": round(self.inlet_temp, 2),
            "u1_flow": round(self.u1_flow, 2),
            "u1_outlet": round(self.u1_outlet, 2),
            "u2_flow": round(self.u2_flow, 2),
            "u2_outlet": round(self.u2_outlet, 2),
            "predicted_trend": round(predicted_trend, 2),
            "baseline_opex": round(baseline_opex, 2),
            "optimized_opex": round(optimized_opex, 2),
            "savings": round(self.total_cumulative_savings, 2)
        }

class PredictiveSupervisor:
    def evaluate(self, state, fault_active):
        if fault_active:
            # Autonomous Routing: Route around fouling by shifting load
            return -0.2, 0.2
        else:
            u1_error = 100.0 - state["u1_outlet"]
            u2_error = 120.0 - state["u2_outlet"]
            
            action_u1 = 0.03 * u1_error
            action_u2 = 0.05 * u2_error
            
            if abs(state["predicted_trend"] - 120.0) > 8.0:
                action_u1 += 0.01
                action_u2 += 0.01
            
            return action_u1, action_u2

if __name__ == "__main__":
    ml_forecaster = TEPMachineLearningForecaster("mode1_normal_500.xlsx")
    plant = FullPlantTEPSimulator(ml_forecaster)
    supervisor = PredictiveSupervisor()
    
    print("Running Upgraded TEP-Integrated Master Simulation...")
    csv_filename = "tep_master_simulation_log.csv"
    
    with open(csv_filename, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["time_min", "carbon_tax", "inlet_temp", "u1_flow", "u1_outlet", "u2_flow", "u2_outlet", "predicted_trend", "baseline_opex", "optimized_opex", "savings"])
        writer.writeheader()
        
        state = plant.step(0.0, 0.0, fault_active=False, dt_min=1.0)
        writer.writerow(state)
        
        active_fault = False
        fault_timer = 0
        disturbance = 0.0
        
        for minute in range(1, 1441):
            roll = random.random()
            if roll < 0.008:
                severity_roll = random.random()
                disturbance = random.choice([-0.8, 0.8]) if severity_roll < 0.70 else random.choice([-4.5, 4.0])
            else:
                disturbance *= 0.90
                
            if not active_fault and random.random() < 0.001:
                active_fault = True
                fault_timer = random.randint(60, 120)
            elif active_fault:
                fault_timer -= 1
                if fault_timer <= 0:
                    active_fault = False
            
            a1, a2 = supervisor.evaluate(state, active_fault)
            state = plant.step(a1, a2, fault_active=active_fault, dt_min=1.0, active_disturbance=disturbance)
            writer.writerow(state)

    print(f"Simulation complete! Telemetry log saved to '{csv_filename}'.")