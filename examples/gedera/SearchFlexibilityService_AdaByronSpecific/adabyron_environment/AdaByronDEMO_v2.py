from adabyron_environment.agents.airConditioning_v2 import Airconditioning
from adabyron_environment.agents.chargingStation_v2 import ChargingStation
from adabyron_environment.agents.storageBattery_v2 import StorageBattery
from adabyron_environment.environment import State
import itertools
import numpy as np
from datetime import datetime

# TODO: Mirar los indices de las energias y los dias


### This is the environment class
### It will be used to create the environment and to interact with it

class AdaByronDEMO():
    """UMA DEMOSITE SCENARIO"""
    metadata = {'render.modes': ['human', 'computer']}

    def __init__(self, 
                 agents, 
                 consumption_curve, 
                 generated_energy, 
                 energy_price_buy,
                 energy_price_sell,
                 season = 0, 
                 temp_range = [21, 23], 
                 outside_temp = 24,
                 starting_temp = 23,
                 expected_saving_percentage = 5,
                 pasive_consumption = 150,
                 simulation = False,
                 verbose = False): # capacity = 120.0, soc = 0.5):
        # Initialize all components        
        self.season             = season # 0 for summer, 1 for winter
        self.env_starting_temp  = starting_temp
        self.temp_range         = temp_range
        self.workinghours = [8, 18]
        self.saving_percentage = expected_saving_percentage
        self.expected_saving_percentage = (100 - expected_saving_percentage)/100
        self.expected_saving_percentage_threshold = min(1, self.expected_saving_percentage + 0.05)

        self.pasive_consumption = pasive_consumption
        
        self.outside_temp        = outside_temp
        
        self.agents = agents
        
        total_actions = []
        suma_total = 0
        
        for agent in self.agents:
            total_actions.append(range(0, agent.get_action_space()))
            suma_total+=agent.get_action_space()

        self.action_space = (suma_total, total_actions)
        
        self.consumption_curve  = consumption_curve
        self.generated_energy   = generated_energy
        self.energy_price_buy   = energy_price_buy
        self.energy_price_sell  = energy_price_sell
        
        self.final_prices_if_not_applying = np.dot(self.consumption_curve, self.energy_price_buy)
        
        self.initial_day_step = datetime.now().hour - 1 if not simulation else -1
        
        self.verbose = verbose
        

        
        
    def reset(self):
        agents_info = {}
        for agent in self.agents:
            agents_info[agent.getName()] = agent.reset()
        
        specific = {
            "actual_temp" : self.env_starting_temp
        }       
        return State(
                agents_info = agents_info,
                specific = specific,
                day_step = self.initial_day_step
            )
        
    
    
    def getAgentsActionSpace(self):
        return [agent.get_action_space() for agent in self.agents]
    
    def checkAction(self, state, action):
        """
        Given a state, it returns a list of possible next states
        Args:
            state: State object
        Returns:
            next_states: list of State
        """
                
        consumption         = self.consumption_curve[state.day_step+1]
        local_temperature   = state.specific["actual_temp"]
        battery_step_consumption = 0
        
        agents_information  = {}
        actions             = {}
        none_returned       = False
        
        # We iterate over the agents and get the consumption and temperature variation
        for i in range(0, len(self.agents)):
            agent_name      = self.agents[i].getName()
            salida_agente   = self.agents[i].step(action, state.agents_info[agent_name])

            if salida_agente is None:
                if self.verbose:
                    print("Combination {} not valid because agent {} returned None".format(action, agent_name))
                none_returned = True
                break


            agents_information[agent_name]  = salida_agente[agent_name]
            actions[agent_name]             = action
            
            if type(self.agents[i]) == Airconditioning:
                agent_deg = salida_agente['temp_change']

                if agent_deg is None:
                    local_temperature = (local_temperature + self.outside_temp)/2
                else:
                    local_temperature += agent_deg
                
            agent_consumption = salida_agente['consumption']
            battery_step_consumption = agent_consumption
            consumption += agent_consumption

        state_cumulative_consumption = consumption + state.cumulative_consumption
        


        
        step_price = consumption*self.energy_price_buy[state.day_step+1] if consumption >= 0 else consumption*self.energy_price_sell[state.day_step+1]
        #base_step_price = self.consumption_curve[state.day_step+1]*self.energy_price_buy[state.day_step+1]
        
        #step_price = step_price - base_step_price
        
        if self.verbose:
            print("Step price: {} consumption: {} energy price: {}".format(step_price, consumption, self.energy_price_buy[state.day_step+1]))
        
        
        cumulative_price = step_price + state.cumulative_price
        
        #If any agent returns None, we don't add the state
        if none_returned:
            return None

        if state.day_step+1 == len(self.energy_price_buy)-1:
            episode_ended = True
        else:
            episode_ended = False 

        return State(father = state,  
                                    consumption = consumption, 
                                    cumulative_consumption = state_cumulative_consumption, 
                                    cumulative_price = cumulative_price,
                                    price=step_price,
                                    episode_ended = episode_ended, 
                                    day_step = state.day_step+1,
                                    actions=actions,
                                    agents_info=agents_information,
                                    specific = {
                                        "actual_temp":local_temperature
                                                })
                
    
    def step(self, state):
        """
        Given a state, it returns a list of possible next states
        Args:
            state: State object
        Returns:
            next_states: list of State
        """
        agent_action_combination =list(itertools.product(*self.action_space[1]))

        next_states = []

        for combination in agent_action_combination:
            if self.verbose:
                print(len(combination))
                print("Trying combination {}".format(combination))
                
            consumption         = self.consumption_curve[state.day_step+1]
            local_temperature   = state.specific["actual_temp"]
            battery_step_consumption = 0
            
            agents_information  = {}
            actions             = {}
            none_returned       = False
            
            # We iterate over the agents and get the consumption and temperature variation
            for i in range(0, len(self.agents)):
                agent_name      = self.agents[i].getName()
                salida_agente   = self.agents[i].step(combination[i], state.agents_info[agent_name])

                if salida_agente is None:
                    if self.verbose:
                        print("Combination {} not valid because agent {} returned None".format(combination, agent_name))
                    none_returned = True
                    break


                agents_information[agent_name]  = salida_agente[agent_name]
                actions[agent_name]             = combination[i]
                
                if type(self.agents[i]) == Airconditioning:
                    agent_deg = salida_agente['temp_change']

                    if agent_deg is None:
                        local_temperature = (local_temperature + self.outside_temp)/2
                    else:
                        local_temperature += agent_deg
                    
                agent_consumption = salida_agente['consumption']
                battery_step_consumption = agent_consumption
                consumption += agent_consumption
                
                # Dada nuestra curva, esta restricción es aplicable
                # No descargue antes de las 9 de la mañana
                if combination[i] >= 7 and state.day_step+1 < 9:
                    none_returned = True
                # No descargue entre las 13 y las 18
                if combination[i] >= 7 and state.day_step+1 >= 13 and state.day_step+1 < 18:
                    none_returned = True
                # No cargue entre las 9 y las 13
                if combination[i] < 7 and combination[i] > 0 and state.day_step+1 >= 9 and state.day_step+1 < 13:
                    none_returned = True
                # No cargue entre las 18 y las 21
                if combination[i] < 7 and combination[i] > 0 and state.day_step+1 >= 18 and state.day_step+1 < 21:
                    none_returned = True
                if combination[i] < 7 and combination[i] > 0 and state.day_step+1 >=21:
                    none_returned = True
                if agents_information[agent_name]['soc'] < self.agents[i].capacity and state.day_step+1 == 9:
                    none_returned = True
                    
                    
            #If any agent returns None, we don't add the state
            if none_returned:
                continue


            state_cumulative_consumption = consumption + state.cumulative_consumption
            


            
            step_price = consumption*self.energy_price_buy[state.day_step+1] if consumption >= 0 else consumption*self.energy_price_sell[state.day_step+1]
            #base_step_price = self.consumption_curve[state.day_step+1]*self.energy_price_buy[state.day_step+1]
            
            #step_price = step_price - base_step_price
            
            if self.verbose:
                print("Step price: {} consumption: {} energy price: {}".format(step_price, consumption, self.energy_price_buy[state.day_step+1]))
            
            
            cumulative_price = step_price + state.cumulative_price
            

            #If the temperature is out of bounds we don't add the state
            if state.day_step+1 >= self.workinghours[0] and state.day_step+1 <= self.workinghours[1]:
                if local_temperature < self.temp_range[0] or local_temperature > self.temp_range[1] and local_temperature >= state.specific["actual_temp"]:
                    if self.verbose:
                        print("Combination {} not valid because the temperature is out of bounds".format(combination))
                    continue
            #If the consumption is out of bounds we don't add the state
            # if consumption < self.generated_energy[state.day_step+1] or consumption > self.consumption_curve[state.day_step+1]*1.15:
            #     print("Concumption {} not valid because the consumption is out of bounds".format(consumption))
            #     continue


            if state.day_step+1 == len(self.energy_price_buy)-1:
                episode_ended = True
                #cosa = self.expected_saving_percentage_threshold*self.final_prices_if_not_applying

                if cumulative_price > self.expected_saving_percentage_threshold*self.final_prices_if_not_applying:
                    continue
                elif cumulative_price < self.expected_saving_percentage*self.final_prices_if_not_applying:
                    if self.verbose:
                        print("Achieved saving of at least {}%".format(self.saving_percentage))
                    pass
                else:
                    saving = 100 - (cumulative_price * 100)/self.final_prices_if_not_applying
                    
                    if self.verbose:
                        print("Not achieved saving of {}% but with {}%".format(self.saving_percentage, saving))
            else:
                episode_ended = False 

            next_states.append(State(father = state,  
                                        consumption = consumption, 
                                        cumulative_consumption = state_cumulative_consumption, 
                                        cumulative_price = cumulative_price,
                                        price=step_price,
                                        episode_ended = episode_ended, 
                                        day_step = state.day_step+1,
                                        actions=actions,
                                        agents_info=agents_information,
                                        specific = {
                                            "actual_temp":local_temperature
                                                    }))
                
        return next_states