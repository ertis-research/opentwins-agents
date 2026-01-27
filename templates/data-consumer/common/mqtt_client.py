"""
MQTT Client Module for Data Consumer
Provides utilities for connecting to and consuming data from MQTT brokers.
"""

import paho.mqtt.client as mqtt
import json
import logging
from typing import Callable, Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MQTTConsumer:
    """MQTT Consumer client for subscribing to topics and handling messages."""
    
    def __init__(self, broker: str, port: int = 1883, client_id: Optional[str] = None,
                 username: Optional[str] = None, password: Optional[str] = None,
                 use_tls: bool = False, ca_certs: Optional[str] = None):
        """
        Initialize MQTT Consumer.
        
        Args:
            broker: MQTT broker address
            port: MQTT broker port (default: 1883)
            client_id: Unique client identifier
            username: MQTT username for authentication
            password: MQTT password for authentication
            use_tls: Enable TLS/SSL encryption
            ca_certs: Path to CA certificates file for TLS
        """
        self.broker = broker
        self.port = port
        self.client_id = client_id or f"consumer_{id(self)}"
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.ca_certs = ca_certs
        
        self.client = mqtt.Client(client_id=self.client_id)
        self.message_callback: Optional[Callable] = None
        self.is_connected = False
        
        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Configure authentication if provided
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        # Configure TLS if enabled
        if self.use_tls:
            self.client.tls_set(ca_certs=self.ca_certs)
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker."""
        if rc == 0:
            self.is_connected = True
            logger.info(f"Connected to MQTT broker at {self.broker}:{self.port}")
        else:
            self.is_connected = False
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker."""
        self.is_connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker. Return code: {rc}")
        else:
            logger.info("Disconnected from MQTT broker")
    
    def _on_message(self, client, userdata, msg):
        """Callback for when a message is received."""
        logger.debug(f"Received message on topic '{msg.topic}': {msg.payload.decode()}")
        
        if self.message_callback:
            try:
                # Try to parse as JSON
                try:
                    payload = json.loads(msg.payload.decode())
                except json.JSONDecodeError:
                    payload = msg.payload.decode()
                
                self.message_callback(msg.topic, payload)
            except Exception as e:
                logger.error(f"Error in message callback: {e}")
    
    def connect(self):
        """Connect to the MQTT broker."""
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            logger.info(f"Connecting to MQTT broker at {self.broker}:{self.port}...")
        except Exception as e:
            logger.error(f"Error connecting to MQTT broker: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from the MQTT broker."""
        self.client.disconnect()
        logger.info("Disconnecting from MQTT broker...")
    
    def subscribe(self, topic: str, qos: int = 0):
        """
        Subscribe to a topic.
        
        Args:
            topic: Topic to subscribe to (supports wildcards: +, #)
            qos: Quality of Service level (0, 1, or 2)
        """
        self.client.subscribe(topic, qos)
        logger.info(f"Subscribed to topic: {topic} (QoS: {qos})")
    
    def set_message_callback(self, callback: Callable[[str, Any], None]):
        """
        Set the callback function for handling incoming messages.
        
        Args:
            callback: Function that takes (topic, payload) as arguments
        """
        self.message_callback = callback
    
    def start(self):
        """Start the MQTT client loop (blocking)."""
        logger.info("Starting MQTT consumer loop...")
        self.client.loop_forever()
    
    def start_background(self):
        """Start the MQTT client loop in a background thread."""
        logger.info("Starting MQTT consumer loop in background...")
        self.client.loop_start()
    
    def stop_background(self):
        """Stop the background MQTT client loop."""
        logger.info("Stopping MQTT consumer background loop...")
        self.client.loop_stop()


def create_mqtt_consumer(config: Dict[str, Any]) -> MQTTConsumer:
    """
    Factory function to create an MQTT consumer from a configuration dictionary.
    
    Args:
        config: Dictionary containing MQTT configuration
               Expected keys: broker, port, client_id, username, password, use_tls, ca_certs
    
    Returns:
        Configured MQTTConsumer instance
    """
    return MQTTConsumer(
        broker=config.get('broker'),
        port=config.get('port', 1883),
        client_id=config.get('client_id'),
        username=config.get('username'),
        password=config.get('password'),
        use_tls=config.get('use_tls', False),
        ca_certs=config.get('ca_certs')
    )
