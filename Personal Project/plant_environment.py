import random

class ContinuousPlantEnvironment:
    def __init__(self):
        self.time_elapsed_hours = 0.0
        self.crude_inlet_temp = 25.0       # °C
        self.crude_mass_flow = 2.78        # kg/s
        self.crude_cp = 2.3                # kJ/kg-K
        self.water_inlet_temp = 180.0      # °C
        self.water_cp = 4.184              # kJ/kg-K
        
        self.utility_flow = 8.0            # kg/s
        self.crude_outlet_temp = 102.9     # °C (Current dynamic state)

    def step(self, action_delta, dt_minutes=1.0, active_disturbance=0.0):
        """
        Advances the plant state continuously in time, incorporating thermal lag 
        and random external disturbances.
        """
        self.time_elapsed_hours += dt_minutes / 60.0
        
        # 1. Apply disturbance to inlet temperature with smoothing (inertia)
        target_inlet = 25.0 + active_disturbance
        self.crude_inlet_temp += (target_inlet - self.crude_inlet_temp) * 0.2
        
        # 2. Update manipulated variable (utility flow) based on agent action
        self.utility_flow += action_delta
        self.utility_flow = max(1.0, min(self.utility_flow, 15.0))
        
        # 3. Calculate steady-state target temperature
        effectiveness = 1.2
        Q_transferred = self.utility_flow * self.water_cp * (self.water_inlet_temp - self.crude_inlet_temp) * 0.08 * effectiveness
        target_outlet = self.crude_inlet_temp + (Q_transferred / (self.crude_mass_flow * self.crude_cp))
        
        # 4. Thermal Lag / First-Order Inertia (Process doesn't change instantly!)
        # The actual temperature catches up to the target temperature gradually over time
        time_constant = 3.0 # minutes
        alpha = dt_minutes / (time_constant + dt_minutes)
        self.crude_outlet_temp += alpha * (target_outlet - self.crude_outlet_temp)
        
        # 5. Scope 1 Emissions & OPEX
        thermal_energy_gj_hr = Q_transferred * 3.6
        scope1_co2_kg_hr = thermal_energy_gj_hr * 50.0
        carbon_cost = (scope1_co2_kg_hr / 1000.0) * 40.0
        utility_cost = self.utility_flow * 15.0
        total_opex = round(carbon_cost + utility_cost, 2)
        
        return {
            "time_hr": round(self.time_elapsed_hours, 2),
            "inlet_temp_c": round(self.crude_inlet_temp, 2),
            "utility_flow_kg_s": round(self.utility_flow, 2),
            "outlet_temp_c": round(self.crude_outlet_temp, 2),
            "scope1_co2_tons_hr": round(scope1_co2_kg_hr / 1000.0, 3),
            "total_opex_hr": total_opex
        }