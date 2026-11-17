import os
from paho.mqtt import client as mqtt_client
from paho.mqtt import subscribe as subscribe
import random

class MessageBrokerController:
    def __init__(self):
        # Target broker information
        # self.BROKER_IP       = os.getenv('BROKER_IP')
        # self.BROKER_PORT     = int(os.getenv('BROKER_PORT')) if os.getenv('BROKER_PORT') != None else None
        # self.BROKER_TOPIC_SEND    = os.getenv('BROKER_TOPIC_SEND')
        # self.BROKER_USERNAME = os.getenv('BROKER_USERNAME')
        # self.BROKER_PASSWORD = os.getenv('BROKER_PASSWORD')
        # self.BROKER_TOPIC_RECIEVE_BATTERY    = os.getenv('BROKER_TOPIC_RECIEVE_BATTERY')
        # self.BROKER_TOPIC_RECIEVE_PRICES_UMA    = os.getenv('BROKER_TOPIC_RECIEVE_PRICES_UMA')
        # self.BROKER_TOPIC_RECIEVE_PRICES_VENTAS = os.getenv('BROKER_TOPIC_RECIEVE_PRICES_VENTAS')    
    
        # Create a client instance 
        
        self.BROKER_IP       = "<MQTT_BROKER_HOST>"
        self.BROKER_PORT     = None
        self.BROKER_TOPIC_SEND    = "gedera/prueba/control/adabyron/toshiba"
        self.BROKER_USERNAME = "<MQTT_USER>"
        self.BROKER_PASSWORD = "<MQTT_PASSWORD>"
        self.BROKER_TOPIC_RECIEVE_BATTERY    = "gedera/adabyron/simulation/battery/ampere01/output"
        self.BROKER_TOPIC_RECIEVE_PRICES_UMA    = "gedera/prices/UMA"
        self.BROKER_TOPIC_RECIEVE_PRICES_VENTAS = "gedera/prices/VENTA"
        
        
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, "test-publisher-sensor")
        #self.client = mqtt_client.Client("test-publisher-sensor")
        if self.BROKER_USERNAME != None and self.BROKER_PASSWORD != None:
            self.client.username_pw_set(username=self.BROKER_USERNAME, password=self.BROKER_PASSWORD)
        if self.BROKER_PORT != None:
            self.client.connect(self.BROKER_IP, self.BROKER_PORT)
        else:
            self.client.connect(self.BROKER_IP)

    def read_from_topic(self, topic):
        msg = subscribe.simple(topic, hostname=self.BROKER_IP, auth = {'username':self.BROKER_USERNAME, 'password':self.BROKER_PASSWORD})
        return msg

    def send_message(self, messages):
        self.client.publish(self.BROKER_TOPIC_SEND, messages)