import random
import csv

class CoupledPreheatPlant:
    def __init__(self):
        self.time_minutes = 0.0
        
        # Unit 1: Primary Heat Exchanger
        self.u1_inlet_temp = 25.0       # °C
        self.u1_utility_flow = 8.0      # kg/s
        self.u1_outlet_temp = 102.9     # °C
        
        # Unit 2: Downstream Trim Heater / Column Feed Preheater
        # Notice how Unit 2's inlet temperature IS Unit 1's outlet temperature! (Process Coupling)
        self.u2_utility_flow = 5.0      # kg/s
        self.u2_outlet_temp = 120.0     # °C

    def step(self, action_u1, action_u2, dt_minutes=1.0, active_disturbance=0.0):
        """
        Simulates two coupled unit operations over a high-resolution time step (dt = 1 minute).
        """
        self.time_minutes += dt_minutes
        
        # 1. Unit 1 Disturbance & Thermal Inertia
        target_inlet = 25.0 + active_disturbance
        self.u1_inlet_temp += (target_inlet - self.u1_inlet_temp) * 0.1 # slower thermal inertia for 1-min steps
        
        self.u1_utility_flow += action_u1
        self.u1_utility_flow = max(1.0, min(self.u1_utility_flow, 15.0))
        
        # Unit 1 Thermodynamics
        water_cp, water_inlet = 4.184, 180.0
        crude_mass, crude_cp = 2.78, 2.3
        
        q1 = self.u1_utility_flow * water_cp * (water_inlet - self.u1_inlet_temp) * 0.08 * 1.2
        target_u1_out = self.u1_inlet_temp + (q1 / (crude_mass * crude_cp))
        
        # Apply time constant lag (alpha for 1-minute steps)
        alpha = dt_minutes / (5.0 + dt_minutes) # 5-minute time constant
        self.u1_outlet_temp += alpha * (target_u1_out - self.u1_outlet_temp)
        
        # 2. Unit 2 (Coupled Downstream Unit)
        # Unit 2 takes Unit 1's outlet temperature as its inlet feed!
        self.u2_utility_flow += action_u2
        self.u2_utility_flow = max(1.0, min(self.u2_utility_flow, 12.0))
        
        q2 = self.u2_utility_flow * water_cp * (water_inlet - self.u1_outlet_temp) * 0.06 * 1.0
        target_u2_out = self.u1_outlet_temp + (q2 / (crude_mass * crude_cp))
        self.u2_outlet_temp += alpha * (target_u2_out - self.u2_outlet_temp)
        
        # 3. Combined Plant Economics & Scope 1 Emissions
        total_q = q1 + q2
        thermal_gj_hr = total_q * 3.6
        scope1_co2_kg_hr = thermal_gj_hr * 50.0
        opex_hr = ((scope1_co2_kg_hr / 1000.0) * 40.0) + ((self.u1_utility_flow + self.u2_utility_flow) * 15.0)
        
        return {
            "time_min": round(self.time_minutes, 1),
            "inlet_temp": round(self.u1_inlet_temp, 2),
            "u1_flow": round(self.u1_utility_flow, 2),
            "u1_outlet": round(self.u1_outlet_temp, 2),
            "u2_flow": round(self.u2_utility_flow, 2),
            "u2_outlet": round(self.u2_outlet_temp, 2),
            "scope1_co2": round(scope1_co2_kg_hr / 1000.0, 3),
            "opex": round(opex_hr, 2)
        }

class MultiAgentSupervisor:
    def decide_actions(self, state, target_temp=120.0):
        # Unit 1 Agent: Focuses on primary preheat target (~100°C)
        u1_error = 100.0 - state["u1_outlet"]
        action_u1 = 0.08 * u1_error + 0.05 * (25.0 - state["inlet_temp"]) # feedforward
        
        # Unit 2 Agent: Focuses on final distillation column feed target ($120^\circ\text{C}$)
        u2_error = target_temp - state["u2_outlet"]
        action_u2 = 0.1 * u2_error
        
        # Economic override if OPEX climbs too high
        if state["opex"] > 4600.0:
            action_u1 -= 0.05
            action_u2 -= 0.05
            
        return action_u1, action_u2

if __name__ == "__main__":
    plant = CoupledPreheatPlant()
    supervisor = MultiAgentSupervisor()
    
    print("=== STARTING COUPLED MULTI-AGENT PLANT SIMULATION (Minute-by-Minute) ===")
    
    # Setup CSV Data Logger
    csv_filename = "plant_simulation_log.csv"
    with open(csv_filename, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["time_min", "inlet_temp", "u1_flow", "u1_outlet", "u2_flow", "u2_outlet", "scope1_co2", "opex"])
        writer.writeheader()
        
        current_disturbance = 0.0
        state = plant.step(0.0, 0.0, dt_minutes=1.0)
        writer.writerow(state)
        
        # Simulate 120 minutes (2 hours) of minute-by-minute plant operations
        for minute in range(1, 121):
            # Stochastic disturbances hit at random minutes
            if random.random() < 0.05: # 5% chance per minute
                current_disturbance = random.choice([-5.0, -3.0, 3.0, 6.0])
                print(f"[!] Minute {minute}: Upstream Disturbance Shock = {current_disturbance:+.1f}°C")
            else:
                current_disturbance *= 0.9 # slow decay
                
            # Agents compute actions
            a1, a2 = supervisor.decide_actions(state)
            
            # Step plant by 1 minute
            state = plant.step(a1, a2, dt_minutes=1.0, active_disturbance=current_disturbance)
            writer.writerow(state)
            
            if minute % 15 == 0: # Print status every 15 minutes
                print(f"Time: {state['time_min']}m | Inlet: {state['inlet_temp']}°C | U1 Out: {state['u1_outlet']}°C | U2 Out (Target 120°C): {state['u2_outlet']}°C | OPEX: ${state['opex']}/hr")

    print(f"\n=== SIMULATION COMPLETE! Data successfully logged to '{csv_filename}' ==.")