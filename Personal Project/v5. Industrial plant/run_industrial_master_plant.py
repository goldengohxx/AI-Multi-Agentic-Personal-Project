import random
import csv
import time
import os

class AdvancedIndustrialMasterPlant:
    def __init__(self):
        self.time_min = 0.0
        
        # Plant States
        self.u1_inlet_temp = 25.0       # °C
        self.u1_utility_flow = 8.0      # kg/s
        self.u1_outlet_temp = 100.0     # °C
        self.u1_status = "NORMAL"       # NORMAL or FAULT_FOULING
        
        self.u2_utility_flow = 5.0      # kg/s
        self.u2_outlet_temp = 120.0     # °C
        
        # Economic & Environmental parameters
        self.carbon_tax_rate = 40.0     # $/ton CO2 (dynamic)
        self.utility_unit_cost = 15.0   # $/kg-s utility cost
        
        # Fault tracking variables
        self.fault_timer = 0

    def step(self, action_u1, action_u2, fault_active=False, dt_min=1.0):
        self.time_min += dt_min
        
        # Dynamic Economic Optimization (Option C): Carbon tax shifts over a 24-hour cycle (1440 mins)
        # Higher carbon tax during peak industrial hours (e.g., hours 4 to 12)
        cycle_time = self.time_min % 1440
        self.carbon_tax_rate = 40.0 + 20.0 * (1.0 if 240 <= cycle_time <= 720 else 0.0)
        
        # Fault handling (Option A)
        if fault_active:
            self.u1_status = "CRITICAL: U1 FOULING BLOCKAGE DETECTED"
            effective_efficiency = 0.35 # Severe thermal drop due to scale buildup
        else:
            self.u1_status = "NORMAL"
            effective_efficiency = 1.2

        # Unit 1 Thermodynamics
        water_cp, water_inlet = 4.184, 180.0
        crude_mass, crude_cp = 2.78, 2.3
        
        self.u1_utility_flow += action_u1
        self.u1_utility_flow = max(1.0, min(self.u1_utility_flow, 15.0))
        
        q1 = self.u1_utility_flow * water_cp * (water_inlet - self.u1_inlet_temp) * 0.08 * effective_efficiency
        target_u1_out = self.u1_inlet_temp + (q1 / (crude_mass * crude_cp))
        
        alpha = dt_min / (5.0 + dt_min)
        self.u1_outlet_temp += alpha * (target_u1_out - self.u1_outlet_temp)
        
        # Unit 2 Trim Heater (Coupled Operation)
        self.u2_utility_flow += action_u2
        self.u2_utility_flow = max(1.0, min(self.u2_utility_flow, 15.0))
        
        # If Unit 1 is fouled, Unit 2 automatically compensates to protect final product temp
        q2 = self.u2_utility_flow * water_cp * (water_inlet - self.u1_outlet_temp) * 0.06 * 1.0
        target_u2_out = self.u1_outlet_temp + (q2 / (crude_mass * crude_cp))
        self.u2_outlet_temp += alpha * (target_u2_out - self.u2_outlet_temp)
        
        # Economics & Emissions
        total_q = q1 + q2
        gj_hr = total_q * 3.6
        co2_tons_hr = (gj_hr * 50.0) / 1000.0
        
        opex_hr = (co2_tons_hr * self.carbon_tax_rate) + ((self.u1_utility_flow + self.u2_utility_flow) * self.utility_unit_cost)
        
        return {
            "time_min": round(self.time_min, 1),
            "status": self.u1_status,
            "inlet_temp": round(self.u1_inlet_temp, 2),
            "u1_flow": round(self.u1_utility_flow, 2),
            "u1_outlet": round(self.u1_outlet_temp, 2),
            "u2_flow": round(self.u2_utility_flow, 2),
            "u2_outlet": round(self.u2_outlet_temp, 2),
            "carbon_tax": round(self.carbon_tax_rate, 1),
            "co2_tons": round(co2_tons_hr, 3),
            "opex": round(opex_hr, 2)
        }

class CognitiveAgentSystem:
    def evaluate(self, state):
        # Fault Detection & Isolation (Option A): Autonomous rerouting when fouling is flagged
        if "FOULING" in state["status"]:
            action_u1 = -0.6  # Back off fouled unit
            action_u2 = 0.5   # Boost trim heater to compensate
        else:
            u1_error = 100.0 - state["u1_outlet"]
            u2_error = 120.0 - state["u2_outlet"]
            
            action_u1 = 0.08 * u1_error
            action_u2 = 0.1 * u2_error
            
            # Dynamic economic carbon penalty mitigation (Option C)
            if state["carbon_tax"] > 50.0:
                action_u1 -= 0.05
                action_u2 -= 0.05
                
        return action_u1, action_u2

def render_hmi_screen(state):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("======================================================================")
    print("  ABB 800xA COGNITIVE DCS HMI | 24-HOUR STOCHASTIC PLANT OPTIMIZER     ")
    print("======================================================================")
    print(f" TIME: {state['time_min']:05.1f} min | STATUS: {state['status']}")
    print(f" CARBON TAX: ${state['carbon_tax']}/ton | EMISSIONS: {state['co2_tons']} t/hr")
    print("----------------------------------------------------------------------")
    print(f" [FEED] In: {state['inlet_temp']}°C ---> [UNIT 1 PREHEATER] Out: {state['u1_outlet']}°C")
    print(f"   |---> Utility Valve 1: {state['u1_flow']} kg/s")
    print("          |")
    print(f"          v ---> [UNIT 2 TRIM HEATER] Out: {state['u2_outlet']}°C (Target: 120°C)")
    print(f"                   |---> Utility Valve 2: {state['u2_flow']} kg/s")
    print("----------------------------------------------------------------------")
    print(f" REAL-TIME HOURLY OPEX: ${state['opex']} / hr")
    print("======================================================================")

if __name__ == "__main__":
    plant = AdvancedIndustrialMasterPlant()
    agent = CognitiveAgentSystem()
    
    print("Initializing 24-Hour Stochastic Master DCS Simulation...")
    time.sleep(1.0)
    
    csv_filename = "stochastic_master_plant.csv"
    with open(csv_filename, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["time_min", "status", "inlet_temp", "u1_flow", "u1_outlet", "u2_flow", "u2_outlet", "carbon_tax", "co2_tons", "opex"])
        writer.writeheader()
        
        state = plant.step(0.0, 0.0, fault_active=False, dt_min=1.0)
        
        active_fault = False
        fault_duration_remaining = 0
        
        # Run for 1,440 minutes (24 full hours)
        for minute in range(1, 1441):
            # Stochastic Fault Injection: Random chance a fouling event starts if not already active
            if not active_fault and random.random() < 0.005: # 0.5% chance per minute
                active_fault = True
                fault_duration_remaining = random.randint(30, 60) # lasts 30 to 60 minutes
                print(f"\n[!] RANDOM FAULT INJECTION at Minute {minute}: Unit 1 Fouling Blockage Triggered!")
                time.sleep(1.0)
                
            if active_fault:
                fault_duration_remaining -= 1
                if fault_duration_remaining <= 0:
                    active_fault = False
                    print(f"\n[!] MAINTENANCE RESOLUTION at Minute {minute}: Unit 1 Cleaned & Restored to Normal.")
                    time.sleep(1.0)
            
            # Agents evaluate state and compute actions
            a1, a2 = agent.evaluate(state)
            
            # Step plant with active fault status
            state = plant.step(a1, a2, fault_active=active_fault, dt_min=1.0)
            writer.writerow(state)
            
            # Render HMI dashboard live every 10 minutes (or every minute if you prefer)
            if minute % 10 == 0:
                render_hmi_screen(state)
                time.sleep(0.02)

    print(f"\n[+] 24-Hour Simulation Complete! Data logged to '{csv_filename}'.")