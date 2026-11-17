import os
from paho.mqtt import client as mqtt_client
from paho.mqtt import subscribe as subscribe
import random
import datetime

class MessageBrokerController:
    def __init__(self):
        # Target broker information
        # self.BROKER_IP       = os.getenv('BROKER_IP')
        # self.BROKER_PORT     = int(os.getenv('BROKER_PORT')) if os.getenv('BROKER_PORT') != None else None
        # self.BROKER_TOPIC    = os.getenv('BROKER_TOPIC')
        # self.BROKER_USERNAME = os.getenv('BROKER_USERNAME')
        # self.BROKER_PASSWORD = os.getenv('BROKER_PASSWORD')
        
        
        self.BROKER_IP       = "<MQTT_BROKER_HOST>"
        self.BROKER_PORT     = None
        self.BROKER_TOPIC    = "gedera/prueba/control/adabyron/mercadosecundario"
        self.BROKER_USERNAME = "<MQTT_USER>"
        self.BROKER_PASSWORD = "<MQTT_PASSWORD>"
        self.BROKER_TOPIC_CURVES = "gedera/cartif/prices/1_month"
        
        # Create a client instance 
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, "test-publisher-sensor")
        if self.BROKER_USERNAME != None and self.BROKER_PASSWORD != None:
            self.client.username_pw_set(username=self.BROKER_USERNAME, password=self.BROKER_PASSWORD)
        if self.BROKER_PORT != None:
            self.client.connect(self.BROKER_IP, self.BROKER_PORT)
        else:
            self.client.connect(self.BROKER_IP)

    def send_message(self, messages):
        self.client.publish(self.BROKER_TOPIC, messages)

    
    def get_curves(self):
        msg = subscribe.simple(self.BROKER_TOPIC_CURVES, hostname=self.BROKER_IP, auth = {'username':self.BROKER_USERNAME, 'password':self.BROKER_PASSWORD})
        return msg