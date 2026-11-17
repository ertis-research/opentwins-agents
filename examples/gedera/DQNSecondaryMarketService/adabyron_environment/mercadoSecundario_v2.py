from __future__ import annotations
import json
from dataclasses import dataclass, field
from adabyron_environment.environment import State

class MercadoSecundario():
    # 1. El servicio, sirviendose de las curvas de prediccion de precio del mercado secundario y de la regulacion subir y bajar
    #    es capaz de abrir un arbol de búsqueda para maximizar las ganancias utilizando la bateria en el mercado secundario.
    # 2. El servicio ofrece la posibilidad de subir o bajar energia de la red en funcion de la potencia de la batería y de su capacidad.
    #    Esta bateria puede cargar a 60kWh y descargar a 100kWh.
    # 3. Luego, en funcion de lo que tenga almacenado destinará toda la potencia posible a subir o bajar energía de la red.
    # 4. Una vez se haya hecho una oferta, vemos que red electrica compra X porcentaje de lo ofertado y calculamos lo ganado en cada paso:
    #    Es decir, lo ganado por ofertar en el mercado, y lo que hemos ganado o perdido por subir o bjar energia de la red.


    
    def __init__(self, preservedEnergy, priceCurve, highCurve, lowCurve, highPercentage, lowPercentage, battery) -> None: 
        # Energy price curve
        self.price_curve        = priceCurve
        self.high_curve         = highCurve # PAGAN
        self.low_curve          = lowCurve # COBRAN
        self.high_percentage    =  highPercentage
        self.low_percentage     = lowPercentage
        
        #Battery
        self.battery =  battery
        
        # Percentage of reserved energy
        self.preserved_energy = preservedEnergy
        
    def reset(self):
        return State(
                    agents_info = {
                        self.battery.getName(): self.battery.reset()
                        }
                    )
    
    def step_dqn(self, state, action):        
        # Establecemos el dia actual
        actual_day = state.day_step + 1
            
        # Ya que solo tenemos un agente, que en este caso es la bateria solo hay que ejecutar uno.
        # Bateria normal
        # TODO: Si vamos a ejecutar mas de una batería, cosa que no es el caso, debemos modificar estas dos lineas para que todas las baterias ejecuten un paso.
        last_battery_data = state.agents_info[self.battery.getName()]
        agent_result, additional_info = self.battery.step(action, last_battery_data) 
        failed_action = False
        # Si el resultado es None significa que no es posible ejecutar esa acción en la batería, por lo que el hipotetico estado no puede crearse,
        # pasando a la siguiente combinacion.
        if agent_result is None:
            failed_action = True
            agent_result = additional_info

        battery_data = agent_result[self.battery.getName()]
        
        # Como el estado es posible, se añade el consumo al anterior.
        consumption = agent_result['consumption']
        reserved_energy = consumption
        # Suponemos que son 0 y en caso de que el consumo sea mayor o menor, es decir, hemos puesto a funcionar la bateria, se modifican.
        real_consumption = 0
        step_price = 0
        
        # En este caso estamos vendiendo
        if consumption < 0:
            real_consumption = consumption * (self.high_percentage[actual_day]/100)
            step_price = real_consumption*self.high_curve[actual_day]*(-1)
            battery_data['soc'] = battery_data['soc'] - consumption + real_consumption
            battery_data['dischargeHistory'] = battery_data['dischargeHistory'] + consumption - real_consumption
        # En este caso estamos comprando    
        elif consumption > 0:
            real_consumption = consumption * (self.low_percentage[actual_day]/100)
            step_price = real_consumption*self.low_curve[actual_day]*(-1)
            battery_data['soc'] = battery_data['soc'] - consumption + real_consumption
            battery_data['chargeHistory'] = battery_data['chargeHistory'] - consumption + real_consumption
        # En caso de que en este momento no vayamos a cargar ni descargar porque no nos convenga, si red electrica no nos va a comprar ni vender, si que es conveniente
        # reservarles la energia, ya que nos pagan por reservarla.
        elif consumption == 0 and self.high_percentage[actual_day] == 0:
            # TODO: Hay que tener en cuenta que a lo mejor no se podria descargar todo, pero por ahora nos vale
            consumption = min(battery_data['soc'], self.battery.maxDischargePower)
        elif consumption == 0 and self.low_percentage[actual_day] == 0:
            # TODO: Hay que tener en cuenta que a lo mejor no se podria cargar todo, pero por ahora nos vale
            consumption = min(self.battery.maxChargePower, self.battery.capacity - battery_data['soc'])
            
        # Hay que calcular el precio por reservar la energia de la cual luego compraran o venderán
        reserve_price = abs(consumption * self.price_curve[actual_day])
            
        step_price = step_price + reserve_price
        cumulative_price = step_price + state.cumulative_price
        
        # Creamos el siguiente estado y establecemos si es final o no.
        
        if failed_action:
            done = True
        else:
            done = True if actual_day == len(self.price_curve)-1 else False
            
        next_state = State(father = state,
                                consumption= real_consumption,
                                cumulative_consumption=state.cumulative_consumption + real_consumption,
                                price=step_price,
                                cumulative_price = cumulative_price, 
                                day_step = actual_day, 
                                episode_ended = done, 
                                agents_info = {
                                    self.battery.getName():battery_data
                                },
                                actions={
                                    self.battery.getName():action
                                },
                                specific={
                                    'reserve_price':reserve_price,
                                    'reserved_energy':reserved_energy
                                })
        # DQN maximizes the reward, for this case we are going to minimize the price so the reward must be the negative of the price
        return next_state, step_price if not failed_action else -1000, done
    
    
    def step(self, state):
        # Take all possible actions of the battery
        list_of_actions = list(range(0,self.battery.get_action_space()))
        
        next_states = []
        # Establecemos el dia actual
        actual_day = state.day_step + 1
        
        for action in list_of_actions:
            
            # Ya que solo tenemos un agente, que en este caso es la bateria solo hay que ejecutar uno.
            # Bateria normal
            # TODO: Si vamos a ejecutar mas de una batería, cosa que no es el caso, debemos modificar estas dos lineas para que todas las baterias ejecuten un paso.
            last_battery_data = state.agents_info[self.battery.getName()]
            agent_result, _ = self.battery.step(action, last_battery_data) 

            # Si el resultado es None significa que no es posible ejecutar esa acción en la batería, por lo que el hipotetico estado no puede crearse,
            # pasando a la siguiente combinacion.
            if agent_result is None:
                continue
            
            battery_data = agent_result[self.battery.getName()]
            
            # Como el estado es posible, se añade el consumo al anterior.
            consumption = agent_result['consumption']
            reserved_energy = consumption
            # Suponemos que son 0 y en caso de que el consumo sea mayor o menor, es decir, hemos puesto a funcionar la bateria, se modifican.
            real_consumption = 0
            step_price = 0
            # En este caso estamos vendiendo
            if consumption < 0:
                real_consumption = consumption * (self.high_percentage[actual_day]/100)
                step_price = real_consumption*self.high_curve[actual_day]*(-1)
                battery_data['soc'] = battery_data['soc'] - consumption + real_consumption
                battery_data['dischargeHistory'] = battery_data['dischargeHistory'] + consumption - real_consumption
            # En este caso estamos comprando    
            elif consumption > 0:
                real_consumption = consumption * (self.low_percentage[actual_day]/100)
                step_price = real_consumption*self.low_curve[actual_day]*(-1)
                battery_data['soc'] = battery_data['soc'] - consumption + real_consumption
                battery_data['chargeHistory'] = battery_data['chargeHistory'] - consumption + real_consumption
            # En caso de que en este momento no vayamos a cargar ni descargar porque no nos convenga, si red electrica no nos va a comprar ni vender, si que es conveniente
            # reservarles la energia, ya que nos pagan por reservarla.
            elif consumption == 0 and self.high_percentage[actual_day] == 0:
                # TODO: Hay que tener en cuenta que a lo mejor no se podria descargar todo, pero por ahora nos vale
                consumption = min(battery_data['soc'], self.battery.maxDischargePower)
            elif consumption == 0 and self.low_percentage[actual_day] == 0:
                # TODO: Hay que tener en cuenta que a lo mejor no se podria cargar todo, pero por ahora nos vale
                consumption = min(self.battery.maxChargePower, self.battery.capacity - battery_data['soc'])
                
            # Hay que calcular el precio por reservar la energia de la cual luego compraran o venderán
            reserve_price = abs(consumption * self.price_curve[actual_day])
                
            step_price = step_price + reserve_price
            cumulative_price = step_price + state.cumulative_price
            
            # Creamos el siguiente estado y establecemos si es final o no.
            if actual_day == len(self.price_curve)-1:
                next_states.append(State(father = state,
                                        consumption= real_consumption,
                                        cumulative_consumption=state.cumulative_consumption + real_consumption,
                                        price=step_price,
                                        cumulative_price = cumulative_price, 
                                        day_step = actual_day, 
                                        episode_ended = True, 
                                        agents_info = {
                                            self.battery.getName():battery_data
                                        },
                                        actions={
                                            self.battery.getName():action
                                        },
                                        specific={
                                            'reserve_price':reserve_price,
                                            'reserved_energy':reserved_energy
                                        }
                                        ))
            else:
                next_states.append(State(father = state,
                                        consumption= real_consumption,
                                        cumulative_consumption=state.cumulative_consumption + real_consumption,
                                        price=step_price,
                                        cumulative_price = cumulative_price, 
                                        day_step = actual_day, 
                                        episode_ended = False, 
                                        agents_info = {
                                            self.battery.getName():battery_data
                                        },
                                        actions={
                                            self.battery.getName():action
                                        },
                                        specific={
                                            'reserve_price':reserve_price,
                                            'reserved_energy':reserved_energy
                                        }))
                
        return next_states