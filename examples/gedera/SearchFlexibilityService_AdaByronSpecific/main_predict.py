
import os
import json
import random
import itertools
import pandas as pd
from datetime import date
import datetime
from queue import PriorityQueue
import matplotlib.pyplot as plt
import influxdb_client, os, time
from itertools import permutations
from search_utils.utils import define_env
from influxdb_client.client.write_api import SYNCHRONOUS
from adabyron_environment.AdaByronDEMO_v2 import AdaByronDEMO
from influxdb_client import InfluxDBClient, Point, WritePrecision
from adabyron_environment.agents.storageBattery_v2 import StorageBattery
from search_utils.message_broker_controller import MessageBrokerController
from search_utils.SearchAlgorithms import LowestSearch_Poda, HighestSearch_Poda


# Reading the data from mqtt broker
mqtt_service = MessageBrokerController()


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

#Getting the current temperature
# INFLUX_TOKEN= os.getenv('INFLUX_TOKEN')
# INFLUX_ORG = os.getenv('INFLUX_ORG')
# INFLUX_URL = os.getenv('INFLUX_URL')

INFLUX_TOKEN= "<INFLUX_TOKEN>"
INFLUX_ORG  = "<INFLUX_ORG>"
INFLUX_URL  = "<INFLUX_URL>"

with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG, timeout=900) as client:
    query = 'from(bucket: "data") \
                |> range(start: 2010-04-30T21:00:00.000Z) \
                |> filter(fn: (r) => r["_measurement"] == "uma_loxone_weather_1") \
                |> filter(fn: (r) => r["_field"] == "val_temperature") \
                |> keep(columns: ["_time", "_value"]) \
                |> last()'
    tables = client.query_api().query(query, org=INFLUX_ORG)
    
    for table in tables:
            for record in table.records:
                temperatura = record["_value"]
                

temperatura = float(temperatura)

season = 0 if datetime.datetime.now().month >= 5 and datetime.datetime.now().month <= 10 else 1

print("Temperature and season readed")

#Servicio de flexibilidad
consump = [499.041978960801,
677.0924118229761,
580.8875512887487,
449.1083138936533,
564.4968951421672,
403.71964293155196,
461.9164543943836,
472.807402710725,
467.0278160372443,
414.4480708413706,
402.0754386252675,
502.52256132711375,
468.71056661876554,
408.59901780657304,
493.1217543623346,
372.2220233739892,
368.056003030696,
448.55304256016615,
616.7932275398842,
533.0211410172343,
478.5059233916002,
405.9155234648304,
501.77614971296987,
527.2055358666007]
generated = [0 for i in range(0, 24)]

servicio_flexibilidad = AdaByronDEMO(agents = [StorageBattery("bateria1", capacity = 120, current_soc = battery_current_soc)], 
                 consumption_curve = consump, 
                 generated_energy = generated, 
                 energy_price_buy = read_data_prices_uma,
                 energy_price_sell = read_data_prices_ventas,
                 season = season, 
                 temp_range = [21, 25], 
                 outside_temp = temperatura, 
                 expected_saving_percentage = 5,
                 pasive_consumption = 150)

initial = servicio_flexibilidad.reset()

resultado_servicio_flexibilidad, mejor_solucion = LowestSearch_Poda(servicio_flexibilidad.reset(), servicio_flexibilidad, 10)

actual = mejor_solucion
print(actual.agents_info)

tmp = []
pr  = []
con = []
act = []
pwr = []

while(actual.father is not None):
    con.append(actual.consumption)
    pr.append(actual.price)
    tmp.append(actual.specific["actual_temp"])
    act.append(actual.actions)
    pwr.append(actual.agents_info["bateria1"]["consumption"])
    actual=actual.father



sending_data = []

current_time = datetime.datetime.now()
current_time = current_time.replace(day = current_time.day+1, hour=0, minute=0, second=0, microsecond=0)

for i in range(len(con)):
    next_time = current_time + datetime.timedelta(hours=1)
    json_dict = {
         "inittime": current_time.strftime("%Y-%m-%dT%H:%M:%S"),
         "endtime": next_time.strftime("%Y-%m-%dT%H:%M:%S"),
         "consumption":con[i],
         "price":pr[i],
         "temperature":tmp[i],
         "actions": act[i],
         "power": pwr[i]
    }
    sending_data.append(json_dict)
    current_time = next_time


sending_data = { "Schedule": sending_data }
print(sending_data)
mqtt_service.send_message(json.dumps(sending_data))