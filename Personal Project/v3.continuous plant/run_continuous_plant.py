from plant_environment import ContinuousPlantEnvironment
import random

class SupervisoryAgentSystem:
    def __init__(self, target_temp=120.0):
        self.target_temp = target_temp

    def evaluate_and_decide(self, state):
        current_temp = state["outlet_temp_c"]
        inlet_temp = state["inlet_temp_c"]
        opex = state["total_opex_hr"]
        
        # Thermal feedback + feedforward correction
        temp_error = self.target_temp - current_temp
        thermal_action = 0.1 * temp_error
        
        inlet_deviation = 25.0 - inlet_temp
        feedforward_action = 0.08 * inlet_deviation
        
        # Economic override if OPEX climbs too high
        economic_action = -0.05 if opex > 4500.0 else 0.0
        
        net_action = thermal_action + feedforward_action + economic_action
        return net_action

if __name__ == "__main__":
    env = ContinuousPlantEnvironment()
    agents = SupervisoryAgentSystem(target_temp=120.0)
    
    print("=== STARTING 24-HOUR CONTINUOUS PLANT DIGITAL TWIN SIMULATION ===")
    
    state = env.step(0.0, dt_minutes=0.0)
    current_disturbance = 0.0
    
    # Simulate 24 continuous time-steps (representing hours or multi-minute blocks)
    for hour in range(1, 25):
        # Random chance of an external plant disturbance occurring at random hours
        if random.random() < 0.3: # 30% chance each hour
            current_disturbance = random.choice([-4.0, -2.5, 2.0, 5.0])
            print(f"\n[!] DISTURBANCE ALERT at Hour {hour}: Upstream feed temperature shifted by {current_disturbance:+.1f}°C")
        else:
            current_disturbance *= 0.5 # Disturbance naturally decays over time if no new shock occurs
            
        # Agents evaluate live continuous state and compute action
        action = agents.evaluate_and_decide(state)
        
        # Advance plant time by 60 minutes
        state = env.step(action, dt_minutes=60.0, active_disturbance=current_disturbance)
        
        print(f"Time: {state['time_hr']:04.1f}h | Inlet: {state['inlet_temp_c']}°C | "
              f"Utility: {state['utility_flow_kg_s']}kg/s | Outlet: {state['outlet_temp_c']}°C | "
              f"OPEX: ${state['total_opex_hr']}/hr | Valve Adj: {action:+.2f}")

    print("\n=== CONTINUOUS SIMULATION COMPLETE ===")