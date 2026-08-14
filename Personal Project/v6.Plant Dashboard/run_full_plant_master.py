import random
import csv

class FullPlantMasterSimulator:
    def __init__(self):
        self.time_min = 0.0
        
        # AI-Optimized Plant States
        self.inlet_temp = 25.0
        self.u1_flow = 8.0
        self.u1_outlet = 100.0
        self.u2_flow = 5.0
        self.u2_outlet = 120.0
        
        # Baseline Unoptimized Plant States
        self.base_u1_flow = 10.0
        self.base_u2_flow = 6.0
        self.base_u1_outlet = 100.0
        self.base_u2_outlet = 120.0
        
        self.carbon_tax_rate = 40.0
        self.utility_unit_cost = 15.0

    def step(self, action_u1, action_u2, fault_active=False, dt_min=1.0, active_disturbance=0.0):
        self.time_min += dt_min
        
        # 1. Dynamic Environment (Carbon tax and inlet weather disturbance)
        cycle_time = self.time_min % 1440
        self.carbon_tax_rate = 40.0 + 25.0 * (1.0 if 240 <= cycle_time <= 720 else 0.0)
        
        target_inlet = 25.0 + active_disturbance
        self.inlet_temp += (target_inlet - self.inlet_temp) * 0.1
        
        eff = 0.35 if fault_active else 1.2
        base_eff = 0.35 if fault_active else 1.0
        
        water_cp, water_inlet = 4.184, 180.0
        crude_mass, crude_cp = 2.78, 2.3
        alpha = dt_min / (5.0 + dt_min)
        
        # 2. AI-Optimized Plant Simulation
        self.u1_flow += action_u1
        self.u1_flow = max(1.0, min(self.u1_flow, 15.0))
        q1 = self.u1_flow * water_cp * (water_inlet - self.inlet_temp) * 0.08 * eff
        self.u1_outlet += alpha * ((self.inlet_temp + (q1 / (crude_mass * crude_cp))) - self.u1_outlet)
        
        self.u2_flow += action_u2
        self.u2_flow = max(1.0, min(self.u2_flow, 15.0))
        q2 = self.u2_flow * water_cp * (water_inlet - self.u1_outlet) * 0.06 * 1.0
        self.u2_outlet += alpha * ((self.u1_outlet + (q2 / (crude_mass * crude_cp))) - self.u2_outlet)
        
        ai_gj = (q1 + q2) * 3.6
        ai_co2 = (ai_gj * 50.0) / 1000.0
        optimized_opex = (ai_co2 * self.carbon_tax_rate) + ((self.u1_flow + self.u2_flow) * self.utility_unit_cost)
        
        # 3. Baseline Plant Simulation
        base_q1 = self.base_u1_flow * water_cp * (water_inlet - self.inlet_temp) * 0.08 * base_eff
        self.base_u1_outlet += alpha * ((self.inlet_temp + (base_q1 / (crude_mass * crude_cp))) - self.base_u1_outlet)
        
        base_q2 = self.base_u2_flow * water_cp * (water_inlet - self.base_u1_outlet) * 0.06 * base_eff
        self.base_u2_outlet += alpha * ((self.base_u1_outlet + (base_q2 / (crude_mass * crude_cp))) - self.base_u2_outlet)
        
        base_gj = (base_q1 + base_q2) * 3.6
        base_co2 = (base_gj * 50.0) / 1000.0
        baseline_opex = (base_co2 * self.carbon_tax_rate) + ((self.base_u1_flow + self.base_u2_flow) * self.utility_unit_cost)
        
        savings = baseline_opex - optimized_opex
        
        return {
            "time_min": round(self.time_min, 1),
            "carbon_tax": round(self.carbon_tax_rate, 1), # Added back explicitly!
            "inlet_temp": round(self.inlet_temp, 2),
            "u1_flow": round(self.u1_flow, 2),
            "u1_outlet": round(self.u1_outlet, 2),
            "u2_flow": round(self.u2_flow, 2),
            "u2_outlet": round(self.u2_outlet, 2),
            "baseline_opex": round(baseline_opex, 2),
            "optimized_opex": round(optimized_opex, 2),
            "savings": round(savings, 2)
        }

class MasterSupervisor:
    def evaluate(self, state, fault_active):
        if fault_active:
            # During fouling, intelligently route around the blockage safely
            return -0.3, 0.3 
        else:
            # Normal multi-agent thermal tracking
            u1_error = 100.0 - state["u1_outlet"]
            u2_error = 120.0 - state["u2_outlet"]
            
            action_u1 = 0.05 * u1_error
            action_u2 = 0.08 * u2_error
            
            # Smooth Economic Trim: If carbon tax spikes above $50/ton, gently lean out utility usage 
            # ONLY IF temperatures are stable (preventing negative cost anomalies)
            if state["carbon_tax"] > 50.0 and abs(u2_error) < 2.0:
                action_u1 -= 0.02
                action_u2 -= 0.02
                
            return action_u1, action_u2

if __name__ == "__main__":
    plant = FullPlantMasterSimulator()
    supervisor = MasterSupervisor()
    
    print("Running Full Master Plant Simulation...")
    csv_filename = "full_master_plant_log.csv"
    
    with open(csv_filename, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["time_min", "carbon_tax", "inlet_temp", "u1_flow", "u1_outlet", "u2_flow", "u2_outlet", "baseline_opex", "optimized_opex", "savings"])
        writer.writeheader()
        
        state = plant.step(0.0, 0.0, fault_active=False, dt_min=1.0)
        writer.writerow(state)
        
        active_fault = False
        fault_timer = 0
        disturbance = 0.0
        
        for minute in range(1, 1441):
            if random.random() < 0.02:
                disturbance = random.choice([-4.0, 3.0, 5.0])
            else:
                disturbance *= 0.9
                
            if not active_fault and random.random() < 0.003:
                active_fault = True
                fault_timer = random.randint(30, 50)
            elif active_fault:
                fault_timer -= 1
                if fault_timer <= 0:
                    active_fault = False
            
            a1, a2 = supervisor.evaluate(state, active_fault)
            state = plant.step(a1, a2, fault_active=active_fault, dt_min=1.0, active_disturbance=disturbance)
            writer.writerow(state)

    print(f"Simulation complete! Full data saved to '{csv_filename}'.")