from adabyron_environment.agents.airConditioning_v2 import Airconditioning
from adabyron_environment.agents.chargingStation_v2 import ChargingStation
from adabyron_environment.agents.storageBattery_v2 import StorageBattery
from adabyron_environment.environment import State
import itertools

### This is the environment class
### It will be used to create the environment and to interact with it

class AdaByronDEMO():
    """UMA DEMOSITE SCENARIO"""
    metadata = {'render.modes': ['human', 'computer']}

    def __init__(self, 
                 agents, 
                 consumption_curve, 
                 generated_energy, 
                 energy_price, 
                 season = 0
                 ): # capacity = 120.0, soc = 0.5):
        # Initialize all components        
        self.season             = season # 0 for summer, 1 for winter
        # self.env_starting_temp  = starting_temp
        # self.temp_range         = temp_range
        # self.outside_temp        = outside_temp
        
        self.agents = agents
        
        total_actions = []
        suma_total = 0
        for agent in self.agents:
            total_actions.append(range(0, agent.get_action_space()))
            suma_total+=agent.get_action_space()

        self.action_space = (suma_total, total_actions)
        
        self.consumption_curve  = consumption_curve
        self.generated_energy   = generated_energy
        self.energy_price       = energy_price
        
        
    def reset(self):
        agents_info = {}
        for agent in self.agents:
            agents_info[agent.getName()] = agent.reset() 

        return State(
                agents_info = agents_info
            )
        
    
    
    def getAgentsActionSpace(self):
        return [agent.get_action_space() for agent in self.agents]
    
    def step(self, state):
        agent_action_combination =list(itertools.product(*self.action_space[1]))

        next_states = []

        for combination in agent_action_combination:
            #print(len(combination))
            #print("Trying combination {}".format(combination))
            consumption             = 0
            #local_temperature   = state.specific["actual_temp"]
            
            agents_information      = {}
            actions                 = {}
            possible_combination    = True
            
            # We iterate over the agents and get the consumption and temperature variation
            for i in range(0, len(self.agents)):
                agent_name      = self.agents[i].getName()
                salida_agente   = self.agents[i].step(combination[i], state.agents_info[agent_name])
                
                # If one of the agent output is none, it means that the combination of actions is not possible, so the algorithm is not adding that combination.
                if salida_agente is None:
                    possible_combination = False
                    break
                
                agents_information[agent_name]  = salida_agente[agent_name]
                actions[agent_name]             = combination[i]
                
                # if type(self.agents[i]) == Airconditioning:
                #     agent_deg = salida_agente['temp_change']

                #     if agent_deg is None:
                #         local_temperature = (local_temperature + self.outside_temp)/2 if self.season == 0 else (local_temperature + self.outside_temp)/2
                #     else:
                #         local_temperature += agent_deg
                    
                agent_consumption = salida_agente['consumption']
                consumption += agent_consumption

            if not possible_combination:
                continue
                
            state_cumulative_consumption = consumption + state.cumulative_consumption
            step_price = consumption*self.energy_price[state.day_step+1]
            cumulative_price = step_price + state.cumulative_price
            
            # #If the temperature is out of bounds we don't add the state
            # if local_temperature < self.temp_range[0] or local_temperature > self.temp_range[1]:
            #     #print("Combination {} not valid because the temperature is out of bounds".format(combination))
            #     continue
            # #If the consumption is out of bounds we don't add the state
            # if consumption < self.generated_energy[state.day_step+1] or consumption > self.consumption_curve[state.day_step+1]:
            #     #print("Concumption {} not valid because the consumption is out of bounds".format(consumption))
            #     continue
            
            if state.day_step+1 == len(self.energy_price)-1:
                next_states.append(State(father = state,  
                                         consumption = consumption, 
                                         cumulative_consumption = state_cumulative_consumption, 
                                         cumulative_price = cumulative_price,
                                         price=step_price,
                                         episode_ended = True, 
                                         day_step = state.day_step+1,
                                         actions=actions,
                                         agents_info=agents_information
                                         ))
            else:
                next_states.append(State(father = state, 
                                         consumption = consumption, 
                                         cumulative_consumption = state_cumulative_consumption, 
                                         cumulative_price = cumulative_price, 
                                         price=step_price,
                                         episode_ended = False, 
                                         day_step = state.day_step+1,
                                         actions=actions,
                                         agents_info=agents_information
                                         ))
                
        return next_states
    
    
#   def render(self, mode='human', close=False):
#         # Render the environment to the screen
#         if mode == 'human':
#             for ac in self.airConditionings:
#                 ac.render()
#             for cs in self.chargingStations:
#                 cs.render()
#             for sb in self.batteries:
#                 sb.render()
#             print("Actual consumption: {}, Cumulative consumption: {}, ENDED: {}, Reward: {}".format(self.consumption, self.cumulative_consumption, self._episode_ended, self.reward))