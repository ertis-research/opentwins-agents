import os
import json
import random
import itertools
import pandas as pd
from datetime import date
import datetime
from queue import PriorityQueue
import matplotlib.pyplot as plt
from itertools import permutations
from search_utils.utils import define_env
from adabyron_environment.AdaByronDEMO_v2 import AdaByronDEMO
from adabyron_environment.agents.storageBattery_v2 import StorageBattery
from search_utils.message_broker_controller import MessageBrokerController
from search_utils.SearchAlgorithms import LowestSearch_Poda, HighestSearch_Poda
import numpy as np

def get_solution(battery_current_soc, read_data_prices_uma, read_data_prices_ventas, expected_consumption, last_temp):
    
    #temperatura = get_data_from_influxdb()
    temperatura = last_temp  # Placeholder for temperature, replace with actual data retrieval if needed

    season = 0 if datetime.datetime.now().month >= 5 and datetime.datetime.now().month <= 10 else 1

    #print("Temperature and season readed")


    generated = [0 for i in range(0, 24)]

    battery_capacity = 90

    servicio_flexibilidad = AdaByronDEMO(agents = [StorageBattery("bateria1", capacity = battery_capacity, current_soc = battery_current_soc)], 
                    consumption_curve = expected_consumption, 
                    generated_energy = generated, 
                    energy_price_buy = read_data_prices_uma,
                    energy_price_sell = read_data_prices_ventas,
                    season = season, 
                    temp_range = [23, 25], 
                    outside_temp = temperatura, 
                    expected_saving_percentage = 5,
                    pasive_consumption = 150,
                    simulation=True)



    resultado_servicio_flexibilidad, mejor_solucion = LowestSearch_Poda(servicio_flexibilidad.reset(), servicio_flexibilidad, 10000000)
    
    return resultado_servicio_flexibilidad, mejor_solucion


#battery_current_soc, read_data_prices_uma, read_data_prices_ventas = get_data_from_mqtt()
read_data_prices_uma = [0.1715,0.1715,0.1715,0.1715,0.1715,0.1715,0.1715,0.1715,0.1715,0.1947,0.1947,0.1947,0.1947,0.1947,0.1715,0.1715,0.1715,0.1715,0.1947,0.1947,0.1947,0.1947,0.1715,0.1715]
read_data_prices_ventas = [0.1718,0.1799,0.1308,0.1274,0.109,0.1066,0.1033,0.1001,0.1,0.1031,0.1077,0.1065,0.1148,0.0566,0.0924,0.092,0.0919,0.0898,0.0409,0.0416,0.0412,0.0424,0.1054,0.1645,0.1756,0.1972,0.1557,0.137]
consump = [82.41666666666667,89.81818181818181,81.91666666666667,81.66666666666667,81.91666666666667,86.33333333333333,90.75,107.41666666666667,113.66666666666667,125.58333333333333,119.5,123.08333333333333,126,130.27272727272728,120,123.91666666666667,116.66666666666667,112.91666666666667,106,93.08333333333333,88.08333333333333,84.58333333333333,84.08333333333333,83.58333333333333]
#consump = [i-70 for i in consump]  # Adjusting consumption values

battery_current_soc = 0
day_consumption = np.dot(consump, read_data_prices_uma)

print("Simulation of 30 days using the flexibility service using just one battery")

all_solutions = []
final_simulated_prices = []
last_temp = 24


start = datetime.datetime.now()
resultado_servicio_flexibilidad, mejor_solucion = get_solution(battery_current_soc, read_data_prices_uma, read_data_prices_ventas, consump, last_temp)
battery_current_soc = mejor_solucion.agents_info["bateria1"]["soc"]



print("If not aplying the algorithm the price would be: {}".format (day_consumption*30))
print("Best solution found with price {}".format(sum(final_simulated_prices)))