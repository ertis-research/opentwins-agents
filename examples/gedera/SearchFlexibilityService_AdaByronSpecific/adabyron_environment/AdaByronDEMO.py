from .airConditioning import Airconditioning
from .chargingStation import ChargingStation
from .storageBattery import StorageBattery
import itertools

# TODO: Hay que terminar de adaptar la bateria al mercado diario, actualmente solo está adaptada al mercado secundario
# TODO: Va a haber un cambio en la interaccion con cada uno de los elementos. Ahora la informacion se almacena en state y todos van a recibir un cambio en sus datos que se almacenaran
# en un diccionario.


### This is the environment class
### It will be used to create the environment and to interact with it
class State():
    def __init__(self, father = None, 
                 env_temp = 0,
                 consumption = 0,
                 cumulative_comsumption = 0,
                 cumulative_price = 0,
                 episode_ended = False,
                 day_step = 0,
                 capacities = {},
                 charges = {},
                 discharges = {},
                 soc = {}):
        # Final solution building
        self.father = father
        self.actual_temp                = env_temp
        
        # Global consumption and price info
        self.consumption                = consumption
        self.cumulative_consumption     = cumulative_comsumption
        self._episode_ended             = episode_ended
        self.cumulative_price           = cumulative_price
        
        self.day_step                   = day_step
        
        # Battery info
        self.capacities                 = capacities
        self.charges                    = charges
        self.discharges                 = discharges
        self.soc                        = soc
        
        
        
    def __lt__(self, other):
        if self.day_step == other.day_step:
            return self.cumulative_price < other.cumulative_price
        elif self.day_step > other.day_step:
            return True
        else:
            return False

    def __gt__(self, other):
        if self.day_step == other.day_step:
            return self.cumulative_price > other.cumulative_price
        elif self.day_step < other.day_step:
            return True
        else:
            return False
        
class AdaByronDEMO():
    """UMA DEMOSITE SCENARIO"""
    metadata = {'render.modes': ['human', 'computer']}

    def __init__(self, 
                 airConditionings, 
                 chargingStations, 
                 batteries, 
                 consumption_curve, 
                 generated_energy, 
                 energy_price, 
                 season = 0, 
                 temp_range = [21, 25], 
                 summer_temp = 30, 
                 winter_temp = 15): # capacity = 120.0, soc = 0.5):
        # Initialize all components
        
        self.airConditionings_list  = airConditionings
        self.chargingStations_list  = chargingStations
        self.batteries_list         = batteries  
        
        self.season             = season # 0 for summer, 1 for winter
        self.env_starting_temp  = 23
        self.temp_range         = temp_range
        
        self.summer_temp        = summer_temp
        self.winter_temp        = winter_temp
        
        self.agents = []
        self.initializeAgents()
        
        total_actions = []
        suma_total = 0
        for agent in self.agents:
            total_actions.append(range(0, agent.get_action_space()))
            suma_total+=agent.get_action_space()

        self.action_space = (suma_total, total_actions)
        
        self.consumption_curve  = consumption_curve
        self.generated_energy   = generated_energy
        self.energy_price       = energy_price
        
        
        
        
    def initializeAgents(self):
        for air in self.airConditionings_list:
            self.agents.append(Airconditioning(air))
        for cs in self.chargingStations_list:
            self.agents.append(ChargingStation(cs))
        for bat in self.batteries_list:
            self.agents.append(StorageBattery(bat))
        
    def reset(self):
        charges     = {}
        discharges  = {}
        capacities  = {}
        soc         = {}
        
        
        
        # Reset the state of the environment to an initial state
        for agent in self.agents:
            agent.reset()
            if isinstance(agent, StorageBattery):
                capacities[agent.storageBatteryID] = agent.capacity
                charges[agent.storageBatteryID] = 0
                discharges[agent.storageBatteryID] = 0
                soc[agent.storageBatteryID] = agent.soc
        
        
        return State(env_temp=self.env_starting_temp, charges=charges, discharges=discharges, soc = soc, capacities = capacities)
        
    def render(self, mode='human', close=False):
        # Render the environment to the screen
        if mode == 'human':
            for ac in self.airConditionings:
                ac.render()
            for cs in self.chargingStations:
                cs.render()
            for sb in self.batteries:
                sb.render()
            print("Actual consumption: {}, Cumulative consumption: {}, ENDED: {}, Reward: {}".format(self.consumption, self.cumulative_consumption, self._episode_ended, self.reward))
    
    def getState(self):
        return self.consumption
    
    def getAgentsActionSpace(self):
        return [agent.get_action_space() for agent in self.agents]
    
    def step(self, state):
        agent_action_combination =list(itertools.product(*self.action_space[1]))

        next_states = []
        cont = 0
        for combination in agent_action_combination:
            #print("Trying combination {}".format(combination))
            consumption = 0
            local_temperature = state.actual_temp
            
            
            # We iterate over the agents and get the consumption and temperature variation
            for i in range(0, len(self.agents)):
                cons, deg = self.agents[i].step(combination[i])
                if deg is None:
                    local_temperature = (local_temperature + self.summer_temp)/2 if self.season == 0 else (local_temperature + self.winter_temp)/2
                else:
                    local_temperature += deg
                consumption += cons

            
                
            state_cumulative_consumption = consumption + state.cumulative_consumption
            step_price = consumption*self.energy_price[state.day_step+1]
            cumulative_price = step_price + state.cumulative_price
            
            #If the temperature is out of bounds we don't add the state
            if local_temperature < self.temp_range[0] or local_temperature > self.temp_range[1]:
                continue
            #If the consumption is out of bounds we don't add the state
            if consumption < self.generated_energy[state.day_step+1] or consumption > self.consumption_curve[state.day_step+1]:
                continue
            
            if state.day_step+1 == len(self.consumption_curve)-1:
                next_states.append(State(father = state, env_temp = local_temperature, consumption = consumption, cumulative_comsumption = state_cumulative_consumption, cumulative_price = cumulative_price, episode_ended = True, day_step = state.day_step+1))
            else:
                next_states.append(State(father = state, env_temp = local_temperature, consumption = consumption, cumulative_comsumption = state_cumulative_consumption, cumulative_price = cumulative_price, episode_ended = False, day_step = state.day_step+1))
                
        return next_states
    
    
