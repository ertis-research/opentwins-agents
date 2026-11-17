from dqn_utils.ESIOS_httpx import ESIOS
from datetime import datetime, timedelta, timezone, date
import pandas as pd
import numpy as np
from cmath import phase
import math
import pytz
import os
import json
import tensorflow as tf
from urllib import request
from adabyron_environment.mercadoSecundario_v2 import MercadoSecundario
from adabyron_environment.agents.storageBattery_mercado_secundario import StorageBatteryMS
from dqn_utils.utils import create_q_model, create_q_model_second_model
from dqn_utils.message_broker_controller import MessageBrokerController


#--------------------- ESIOS ---------------------#
#esios_token = os.getenv('ESIOS_TOKEN')
esios_token = "<ESIOS_TOKEN>"
esios = ESIOS(esios_token)

influx_indicator_id = {
    634: "BandaSecundaria",
    682: "RegulacionSubir",
    683: "RegulacionBajar"
}


################# MAIN ######################

def main():
    print("Starting the DQN Flexibility Service...")
    print("Retrieving curves from the message broker...")
    mqtt_controller = MessageBrokerController()
    print("Created mqtt client")
    mensajes = mqtt_controller.get_curves()
    print("Curves retrieved:")
    print(mensajes.payload.decode())
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
    # # Get the list of available series
    # indicators_ = list()
    # indicators_.append(634)
    # indicators_.append(682)
    # indicators_.append(683)

    # #price_curves = esiosDataRetriever(indicators_)
    # curves = localData()

    # message_to_send = predictActions(curves)

    # send_to_mqtt(message_to_send)
    
################# ESIOS ######################

def esiosDataRetriever(indicators):  
   
    indicators_names = esios.get_names(indicators)
    print(indicators_names)
    #Año, mes, día

    start_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = start_time+timedelta(days=2)
    #Get today date

    price_curves = {}

    for indicator in list(indicators_names.keys()):
        print("Retrieving data for {} from {}, to {}.".format(indicator, start_time, end_time))


        df_list, names = esios.get_multiple_series([indicator], start_time, end_time)
        df_list = df_list[0]

        print(df_list)
        
        newDf = df_list.copy().reset_index()

        newDf.drop(["datetime_utc", "tz_time", "geo_id", "geo_name"], axis=1, inplace=True)

        newDf["datetime"] = pd.to_datetime(newDf["datetime"])
        newDf = newDf.groupby(newDf["datetime"].dt.hour).sum(numeric_only=True)

        price_curves[indicators_names[indicator]] = newDf[names[0]].values.tolist()

    
    return price_curves

def localData():
    datee = datetime.now()
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

    bandaSecundaria_df = pd.read_csv('test_data/bandaSecundaria.csv', sep=';')
    regulacionSubir_df = pd.read_csv('test_data/regulacionSubir.csv', sep=';')
    regulacionBajar_df = pd.read_csv('test_data/regulacionBajar.csv', sep=';')
    porcentajeSubir_df = pd.read_csv('test_data/porcentajeSubir.csv', sep=';')
    porcentajeBajar_df = pd.read_csv('test_data/porcentajeBajar.csv', sep=';')


    bandaSecundaria = bandaSecundaria_df[meses[datee.month]]
    regulacionSubir = regulacionSubir_df[meses[datee.month]]
    regulacionBajar = regulacionBajar_df[meses[datee.month]]
    porcentajeSubir = porcentajeSubir_df[meses[datee.month]]
    porcentajeBajar = porcentajeBajar_df[meses[datee.month]]

    return {"BandaSecundaria": bandaSecundaria, "RegulacionSubir": regulacionSubir, "RegulacionBajar": regulacionBajar, "PorcentajeSubir": porcentajeSubir, "PorcentajeBajar": porcentajeBajar}

def predictActions(curves):
    energy_fixed_input = np.array([curves["BandaSecundaria"], curves["RegulacionSubir"], curves["RegulacionBajar"], curves["PorcentajeSubir"], curves["PorcentajeBajar"]]).flatten()


    battery_capacity = 36
    test_battery = StorageBatteryMS("B1",capacity= battery_capacity, original_soc = 23)
    
    mercadoSecundario = MercadoSecundario(preservedEnergy=0.50, 
                                            priceCurve= curves["BandaSecundaria"], 
                                            highCurve=  curves["RegulacionSubir"], 
                                            lowCurve= curves["RegulacionBajar"],
                                            highPercentage= curves["PorcentajeSubir"],
                                            lowPercentage= curves["PorcentajeBajar"],
                                            battery= test_battery)
    total_actions = test_battery.get_action_space()


    #################################################
    ######### DQN MODEL INITIALIZATION ##############
    #################################################

    model = create_q_model_second_model(total_actions)

    model.load_weights("models/gedera_model.h5")


    #################################################
    ######### DQN TRAINING ##########################
    #################################################
    history = []
    action_history = []
    proto_state = mercadoSecundario.reset()

    state = [proto_state.day_step, proto_state.cumulative_consumption, proto_state.cumulative_price, proto_state.agents_info['B1']['soc'], battery_capacity, proto_state.agents_info['B1']['chargeHistory'], proto_state.agents_info['B1']['dischargeHistory']] + energy_fixed_input.tolist()
    history.append(proto_state)
    while True:
        state_tensor = tf.convert_to_tensor([state])
        action_probs = model(state_tensor, training=False)
        action = tf.argmax(action_probs[0]).numpy()

        action_history.append(test_battery.get_action_name(action))  
        # Apply the sampled action in our environment
        proto_state_next, reward, done = mercadoSecundario.step_dqn(proto_state, action)
        history.append(proto_state_next)
        state_next = [proto_state_next.day_step, proto_state_next.cumulative_consumption, proto_state_next.cumulative_price, proto_state_next.agents_info['B1']['soc'], battery_capacity, proto_state_next.agents_info['B1']['chargeHistory'], proto_state_next.agents_info['B1']['dischargeHistory']] + energy_fixed_input.tolist()
        state       = state_next
        proto_state = proto_state_next
                
        if done: break


    soc = []
    cumulative_price = []
    for state in history:
        soc.append(float(state.agents_info["B1"]["soc"]))
        cumulative_price.append(float(state.cumulative_price))

    message_to_send = {
        "benefit": max(cumulative_price),
        "soc": soc,
        "cumulative_price": cumulative_price,
        "actions": action_history
    }

    return message_to_send

def send_to_mqtt(message_to_send):
    mqtt_controller = MessageBrokerController()
    mqtt_controller.send_message(json.dumps(message_to_send))


if __name__ == "__main__":
    main()