from plant_environment import CrudePreheatEnvironment

class SupervisoryAgent:
    def __init__(self, target_temp=120.0):
        self.target_temp = target_temp

    def decide_action(self, current_state):
        current_temp = current_state["crude_outlet_temp_c"]
        temp_error = self.target_temp - current_temp # Positive if too cold, negative if too hot
        
        # If too cold, increase utility flow. If too hot, decrease it.
        action_delta = 0.2 * temp_error
        
        # Clamp action size for smooth control
        action_delta = max(-0.8, min(action_delta, 0.8))
        return action_delta

if __name__ == "__main__":
    env = CrudePreheatEnvironment()
    agent = SupervisoryAgent(target_temp=120.0)
    
    # Initialize state (start cold so agent has to heat it up to target)
    env.utility_flow = 2.0 
    state = env.get_state()
    
    print("=== STARTING AUTONOMOUS PROCESS OPTIMIZATION LOOP ===")
    print(f"Target Crude Outlet Temperature: 120.0 °C\n")
    
    for cycle in range(1, 20):
        print(f"--- Control Cycle {cycle} ---")
        print(f"  [Current Plant State] Utility Flow: {state['utility_flow_kg_s']} kg/s | "
              f"Outlet Temp: {state['crude_outlet_temp_c']} °C | "
              f"Scope 1 Emissions: {state['scope1_co2_tons_hr']} tons CO2/hr")
        
        action = agent.decide_action(state)
        print(f"  [Supervisory Agent] Recommended Utility Adjustment: {action:+.2f} kg/s")
        
        state = env.step(action)
        
    print("\n=== OPTIMIZATION COMPLETE ===")
    print(f"Optimized Final State -> Utility Flow: {state['utility_flow_kg_s']} kg/s, "
          f"Outlet Temp: {state['crude_outlet_temp_c']} °C, "
          f"Scope 1 Emissions: {state['scope1_co2_tons_hr']} tons CO2/hr")