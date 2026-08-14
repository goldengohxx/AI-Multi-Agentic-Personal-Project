from plant_environment import CrudePreheatEnvironment
import random

class ThermalAgent:
    """Agent responsible for thermodynamic stability with feedforward disturbance rejection."""
    def compute_action(self, state, target_temp=120.0):
        current_temp = state["crude_outlet_temp_c"]
        inlet_temp = state["crude_inlet_temp_c"]
        
        # Feedback error control
        temp_error = target_temp - current_temp
        feedback_action = 0.15 * temp_error
        
        # Feedforward compensation: If inlet temp drops below normal (25°C), 
        # proactively add more utility flow before the outlet temp crashes.
        inlet_deviation = 25.0 - inlet_temp
        feedforward_action = 0.1 * inlet_deviation
        
        total_action = feedback_action + feedforward_action
        return total_action, feedforward_action

class EconomicEmissionsAgent:
    """Agent responsible for carbon tax auditing and economic constraint overrides."""
    def audit_costs(self, state):
        co2_tons = state["scope1_co2_tons_hr"]
        carbon_cost_hr = co2_tons * 40.0       # $40 / ton CO2 tax
        utility_cost_hr = state["utility_flow_kg_s"] * 15.0 # Utility cost
        total_opex = carbon_cost_hr + utility_cost_hr
        
        # Economic penalty override if OPEX is burning too high
        cost_penalty_signal = -0.08 if total_opex > 4500.0 else 0.0
        return round(total_opex, 2), cost_penalty_signal

if __name__ == "__main__":
    env = CrudePreheatEnvironment()
    thermal_agent = ThermalAgent()
    economic_agent = EconomicEmissionsAgent()
    
    state = env.reset()
    print("=== OPTION 1: MULTI-AGENT DISTURBANCE REJECTION TEST ===")
    
    # Simulate an unpredictable plant shift where crude inlet temp drops sharply
    # (e.g., cold weather front or upstream storage tank transition)
    disturbances = [-3.0, -2.0, 1.0, 4.0, -1.5]
    
    for cycle, disturbance in enumerate(disturbances, start=1):
        print(f"\n--- Control Cycle {cycle} ---")
        print(f"  [Plant Disturbance] Upstream Crude Inlet Temp Shift: {disturbance:+.1f} °C "
              f"(New Inlet Temp: {state['crude_inlet_temp_c'] + disturbance:.2f} °C)")
        
        # 1. Thermal agent computes action with feedforward compensation
        thermal_action, ff_signal = thermal_agent.compute_action(state)
        
        # 2. Economic agent audits OPEX
        total_opex, eco_action = economic_agent.audit_costs(state)
        print(f"  [Economic Agent] Hourly OPEX: ${total_opex} | Carbon Tax Load: {state['scope1_co2_tons_hr']} tons/hr")
        print(f"  [Thermal Agent] Feedforward Compensation for Inlet Shift: {ff_signal:+.2f} kg/s")
        
        # 3. Multi-agent consensus
        net_action = thermal_action + eco_action
        print(f"  [Consensus] Net Utility Valve Adjustment: {net_action:+.2f} kg/s")
        
        # 4. Step environment with both the agent action and the random disturbance
        state = env.step(net_action, external_disturbance=disturbance)
        print(f"  [Resulting State] Utility Flow: {state['utility_flow_kg_s']} kg/s | "
              f"Outlet Temp: {state['crude_outlet_temp_c']} °C")
              
    print("\n=== DISTURBANCE REJECTION SIMULATION COMPLETE ===")