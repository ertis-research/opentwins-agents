from __future__ import annotations
import json
from dataclasses import dataclass, field


class MercadoSecundario():
    # 1. Segun el documento (a fecha de 22/04/2024) el servicio dedice cuando vender y cuando comprar la energía reservada.
    # 2. De por sí, el tener energía reservada hace que nos reporte beneficio.add()
    # 3. 
    @dataclass(eq=True, order=True)
    class State():
        father:MercadoSecundario.State = field(compare=False)
        cumulative_price:float
        day_step:int
        _episode_ended:bool = field(compare=False)
        battery_info:dict[str,object] = field(compare=False)
        action:int = field(compare=False)
    
        # La clase State servirá para ir abriendo el arbol de búsqueda.
        # def __init__(self, father, totalMoney, dayStep, episodeEnded, batteryInfo) -> None:
        #     self.father = father
        #     self.cumulative_price = totalMoney
        #     self.day_step = dayStep
        #     self._episode_ended = episodeEnded
        #     self.battery_info = batteryInfo
            
        
        
        # def __lt__(self, other):
        #     if self.day_step == other.day_step:
        #         return self.cumulative_price < other.cumulative_price
        #     elif self.day_step > other.day_step:
        #         return True
        #     else:
        #         return False

        # def __gt__(self, other):
        #     if self.day_step == other.day_step:
        #         return self.cumulative_price > other.cumulative_price
        #     elif self.day_step < other.day_step:
        #         return True
        #     else:
        #         return False
        # def __str__(self):
            
        #     return json.dumps({
        #             "father" : self.father,
        #             "cumulative_price" : self.cumulative_price,
        #             "day_step" : self.day_step,
        #             "_episode_ended" : self._episode_ended,
        #             "battery_info" : self.battery_info
        #             })

    
    def __init__(self, preservedEnergy, priceCurve, highPrice, lowCurve, rangesToSell, battery) -> None: 
        # Energy price curve
        self.price_curve = priceCurve
        self.high_price = highPrice
        self.low_curve = lowCurve
        
        # Time ranges to sell energy
        self.ranges_to_sell = rangesToSell
        
        #Battery
        self.battery =  battery
        
        # Percentage of reserved energy
        self.preserved_energy = preservedEnergy
        
        # First state
        self.root_state = self.State(None, 
                            cumulative_price = self.battery.capacity*self.preserved_energy*priceCurve[0],
                            day_step = 0,
                            _episode_ended = False,
                            battery_info = self.battery.reset(),
                            action = None)
        
    def preserve(self):
        pass
    def sell(self):
        pass
    def step(self, state):
        # Take all possible actions of the battery
        list_of_actions = list(range(0,self.battery.get_action_space()))
        
        next_states = []
        # Establecemos el dia actual
        actual_day = state.day_step + 1
        
        for action in list_of_actions:
            
            # Ya que solo tenemos un agente, que en este caso es la bateria solo hay que ejecutar uno.
            agent_result = self.battery.step(action, state.battery_info)
            # Si el resultado es None significa que no es posible ejecutar esa acción en la batería, por lo que el hipototico estado no puede crearse,
            # pasando a la siguiente combinacion.
            if agent_result is None:
                continue
            
            # Como el estado es posible, se añade el consumo al anterior.
            consumption = agent_result['consumption']
            if consumption < 0:
                step_price = (-consumption)*self.low_curve[actual_day]
            else:
                step_price = consumption*self.high_price[actual_day]
            cumulative_price = step_price + state.cumulative_price
            
            
            # Creamos el siguiente estado y establecemos si es final o no.
            if actual_day == len(self.price_curve)-1:
                next_states.append(self.State(father = state, 
                                              cumulative_price = cumulative_price, 
                                              day_step = actual_day, 
                                              _episode_ended = True, 
                                              battery_info = agent_result[self.battery.getStorageBatteryID()],
                                              action=action))
            else:
                next_states.append(self.State(father = state, 
                                              cumulative_price = cumulative_price, 
                                              day_step = actual_day, 
                                              _episode_ended = False, 
                                              battery_info = agent_result[self.battery.getStorageBatteryID()],
                                              action=action))
                
        return next_states