"""
MQTT Client Module for Data Producer
Provides utilities for connecting to and publishing data to MQTT brokers.
"""

import paho.mqtt.client as mqtt
import json
import logging
from typing import Any, Optional, Dict
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MQTTProducer:
    """MQTT Producer client for publishing messages to topics."""
    
    def __init__(self, broker: str, port: int = 1883, client_id: Optional[str] = None,
                 username: Optional[str] = None, password: Optional[str] = None,
                 use_tls: bool = False, ca_certs: Optional[str] = None):
        """
        Initialize MQTT Producer.
        
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
        self.client_id = client_id or f"producer_{id(self)}"
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.ca_certs = ca_certs
        
        self.client = mqtt.Client(client_id=self.client_id)
        self.is_connected = False
        
        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        
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
    
    def _on_publish(self, client, userdata, mid):
        """Callback for when a message is published."""
        logger.debug(f"Message {mid} published successfully")
    
    def connect(self):
        """Connect to the MQTT broker."""
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.is_connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if not self.is_connected:
                raise TimeoutError("Failed to connect to MQTT broker within timeout")
            
            logger.info(f"Connected to MQTT broker at {self.broker}:{self.port}")
        except Exception as e:
            logger.error(f"Error connecting to MQTT broker: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from the MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("Disconnected from MQTT broker")
    
    def publish(self, topic: str, payload: Any, qos: int = 0, retain: bool = False,
                serialize_json: bool = True) -> mqtt.MQTTMessageInfo:
        """
        Publish a message to a topic.
        
        Args:
            topic: Topic to publish to
            payload: Message payload (will be JSON-serialized if serialize_json=True)
            qos: Quality of Service level (0, 1, or 2)
            retain: Whether the message should be retained by the broker
            serialize_json: Whether to serialize payload as JSON
        
        Returns:
            MQTTMessageInfo object
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to MQTT broker")
        
        # Serialize payload if needed
        if serialize_json and not isinstance(payload, (str, bytes)):
            payload = json.dumps(payload)
        
        if isinstance(payload, str):
            payload = payload.encode()
        
        result = self.client.publish(topic, payload, qos=qos, retain=retain)
        logger.debug(f"Published message to topic '{topic}': {payload[:100]}")
        
        return result
    
    def publish_dict(self, topic: str, data: Dict[str, Any], qos: int = 0, 
                    retain: bool = False) -> mqtt.MQTTMessageInfo:
        """
        Publish a dictionary as JSON to a topic.
        
        Args:
            topic: Topic to publish to
            data: Dictionary to publish
            qos: Quality of Service level
            retain: Whether the message should be retained
        
        Returns:
            MQTTMessageInfo object
        """
        return self.publish(topic, data, qos=qos, retain=retain, serialize_json=True)
    
    def publish_batch(self, messages: list[tuple[str, Any]], qos: int = 0, 
                     retain: bool = False, serialize_json: bool = True):
        """
        Publish multiple messages in batch.
        
        Args:
            messages: List of (topic, payload) tuples
            qos: Quality of Service level
            retain: Whether messages should be retained
            serialize_json: Whether to serialize payloads as JSON
        """
        for topic, payload in messages:
            self.publish(topic, payload, qos=qos, retain=retain, 
                        serialize_json=serialize_json)
        
        logger.info(f"Published {len(messages)} messages in batch")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def create_mqtt_producer(config: Dict[str, Any]) -> MQTTProducer:
    """
    Factory function to create an MQTT producer from a configuration dictionary.
    
    Args:
        config: Dictionary containing MQTT configuration
               Expected keys: broker, port, client_id, username, password, use_tls, ca_certs
    
    Returns:
        Configured MQTTProducer instance
    """
    return MQTTProducer(
        broker=config.get('broker'),
        port=config.get('port', 1883),
        client_id=config.get('client_id'),
        username=config.get('username'),
        password=config.get('password'),
        use_tls=config.get('use_tls', False),
        ca_certs=config.get('ca_certs')
    )
