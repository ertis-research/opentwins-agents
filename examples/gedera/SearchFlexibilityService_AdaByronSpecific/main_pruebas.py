
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

# Reading the data from mqtt broker
mqtt_service = MessageBrokerController()


def get_data_from_mqtt():
    #Battery
    read_data_battery = mqtt_service.read_from_topic(mqtt_service.BROKER_TOPIC_RECIEVE_BATTERY)
    battery_current_soc = None

    print("Battery data readed")

    read_data_battery = json.loads(read_data_battery.payload)
    battery_current_soc = read_data_battery["SimulatedBatterySoC"]

    read_data_prices_uma = mqtt_service.read_from_topic(mqtt_service.BROKER_TOPIC_RECIEVE_PRICES_UMA)
    read_data_prices_uma = json.loads(read_data_prices_uma.payload)
    read_data_prices_uma = read_data_prices_uma[4:]
    read_data_prices_uma = [i["value"] for i in read_data_prices_uma]


    read_data_prices_ventas = mqtt_service.read_from_topic(mqtt_service.BROKER_TOPIC_RECIEVE_PRICES_VENTAS)
    read_data_prices_ventas = json.loads(read_data_prices_ventas.payload)
    read_data_prices_ventas = read_data_prices_ventas[4:]
    read_data_prices_ventas = [i["value"] for i in read_data_prices_ventas]

    print("Prices readed")
    
    return battery_current_soc, read_data_prices_uma, read_data_prices_ventas

# def get_data_from_influxdb():

#     #Getting the current temperature
#     INFLUX_TOKEN= "<INFLUX_TOKEN>"
#     INFLUX_ORG = "<INFLUX_ORG>"
#     INFLUX_URL = "<INFLUX_URL>"

#     with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG, timeout=900) as client:
#         query = 'from(bucket: "data") \
#                     |> range(start: 2010-04-30T21:00:00.000Z) \
#                     |> filter(fn: (r) => r["_measurement"] == "uma_loxone_weather_1") \
#                     |> filter(fn: (r) => r["_field"] == "val_temperature") \
#                     |> keep(columns: ["_time", "_value"]) \
#                     |> last()'
#         tables = client.query_api().query(query, org=INFLUX_ORG)
        
#         for table in tables:
#                 for record in table.records:
#                     temperatura = record["_value"]
                    

#     temperatura = float(temperatura)
    
#     return temperatura



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


if __name__ == "__main__":
    
    #battery_current_soc, read_data_prices_uma, read_data_prices_ventas = get_data_from_mqtt()
    read_data_prices_uma = [0.1715,0.1715,0.1715,0.1715,0.1715,0.1715,0.1715,0.1715,0.1715,0.1947,0.1947,0.1947,0.1947,0.1947,0.1715,0.1715,0.1715,0.1715,0.1947,0.1947,0.1947,0.1947,0.1715,0.1715]
    # read_data_prices_uma = [82.953,78.927,77.152,77.288,80.416,84.577,91.944,97.359,83.236,77.145,63.220,49.705,47.802,46.543,54.777,71.838,86.377,101.062,106.622,106.988,105.736,101.136,95.289,89.009]
    # read_data_prices_uma = [i/1000 for i in read_data_prices_uma]  # Convert to kWh prices
    
    read_data_prices_ventas = [0.1718,0.1799,0.1308,0.1274,0.109,0.1066,0.1033,0.1001,0.1,0.1031,0.1077,0.1065,0.1148,0.0566,0.0924,0.092,0.0919,0.0898,0.0409,0.0416,0.0412,0.0424,0.1054,0.1645,0.1756,0.1972,0.1557,0.137]
    consump = [82.41666666666667,89.81818181818181,81.91666666666667,81.66666666666667,81.91666666666667,86.33333333333333,90.75,107.41666666666667,113.66666666666667,125.58333333333333,119.5,123.08333333333333,126,130.27272727272728,120,123.91666666666667,116.66666666666667,112.91666666666667,106,93.08333333333333,88.08333333333333,84.58333333333333,84.08333333333333,83.58333333333333]
    consump = [i-70 for i in consump]  # Adjusting consumption values
    
    battery_current_soc = 50
    day_consumption = np.dot(consump, read_data_prices_uma)

    print("Simulation of 30 days using the flexibility service using just one battery")
    
    all_solutions = []
    final_simulated_prices = []
    last_temp = 24
    for i in range(0, 3):
        print("Simulating day {}".format(i))
        start = datetime.datetime.now()
        resultado_servicio_flexibilidad, mejor_solucion = get_solution(battery_current_soc, read_data_prices_uma, read_data_prices_ventas, consump, last_temp)
        battery_current_soc = mejor_solucion.agents_info["bateria1"]["soc"]
        last_temp = mejor_solucion.specific["actual_temp"]
        all_solutions.append(mejor_solucion)
        final_simulated_prices.append(mejor_solucion.cumulative_price)
        
        print("Se ha tardado {} segundos en simular el dia {}".format((datetime.datetime.now() - start).total_seconds(), i))
        
    print("Simulation finished")
    
    
    print("If not aplying the algorithm the price would be: {}".format (day_consumption*30))
    print("Best solution found with price {}".format(sum(final_simulated_prices)))
    
    
    with open("ada_byron_specific_no_servers.json", "w") as f:
        json.dump([sol.to_dict() for sol in all_solutions], f, indent=4)


# if __name__ == "__main__":
    
#     battery_current_soc, read_data_prices_uma, read_data_prices_ventas = get_data_from_mqtt()
    
#     consump = [82.41666666666667,89.81818181818181,81.91666666666667,81.66666666666667,81.91666666666667,86.33333333333333,90.75,107.41666666666667,113.66666666666667,125.58333333333333,119.5,123.08333333333333,126,130.27272727272728,120,123.91666666666667,116.66666666666667,112.91666666666667,106,93.08333333333333,88.08333333333333,84.58333333333333,84.08333333333333,83.58333333333333]
#     consump = [i-70 for i in consump]
#     print(sum(consump))
#     day_consumption = np.dot(consump, read_data_prices_uma)

    
#     all_solutions = []
#     resultado_servicio_flexibilidad, mejor_solucion = get_solution(battery_current_soc, read_data_prices_uma, read_data_prices_ventas, consump)
#     all_solutions.append(mejor_solucion)
#     print("Simulation finished")
    
#     print("Aplicando sin servidores")

#     print(mejor_solucion.cumulative_price)
#     print(mejor_solucion.cumulative_consumption)
    
#     consump = [82.41666666666667,89.81818181818181,81.91666666666667,81.66666666666667,81.91666666666667,86.33333333333333,90.75,107.41666666666667,113.66666666666667,125.58333333333333,119.5,123.08333333333333,126,130.27272727272728,120,123.91666666666667,116.66666666666667,112.91666666666667,106,93.08333333333333,88.08333333333333,84.58333333333333,84.08333333333333,83.58333333333333]
#     resultado_servicio_flexibilidad, mejor_solucion = get_solution(battery_current_soc, read_data_prices_uma, read_data_prices_ventas, consump)
#     print("Aplicando con servidores")
    
#     print(mejor_solucion.cumulative_price)
#     print(mejor_solucion.cumulative_consumption)
    
#     print("Sin aplicar")
#     real_prices = [0.1715, 0.1715, 0.1715,0.1715, 0.1715, 0.1715, 0.1715, 0.1715, 0.1947,0.1715,0.1715, 0.1715, 0.1715,0.1715, 0.1947, 0.1947, 0.1947, 0.1947,0.1715,0.1715,0.1715, 0.1715, 0.1947, 0.1947]
    
    
#     print(np.dot(consump, real_prices))
#     print(sum(consump))