"""
MQTT Consumer Template
Template for consuming data from MQTT topics.
"""

import logging
import json
from common import MQTTConsumer, load_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MQTTDataConsumer:
    """MQTT data consumer agent."""
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the MQTT consumer.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        
        # Initialize MQTT consumer
        mqtt_config = self.config.get('mqtt', {})
        self.mqtt_client = MQTTConsumer(
            broker=mqtt_config.get('broker', 'localhost'),
            port=mqtt_config.get('port', 1883),
            client_id=mqtt_config.get('client_id', 'mqtt_consumer'),
            username=mqtt_config.get('username'),
            password=mqtt_config.get('password')
        )
        
        # Set message callback
        self.mqtt_client.set_message_callback(self.on_message)
        
        # Get topics to subscribe to
        self.topics = self.config.get('topics', ['sensors/#'])
        
        logger.info("MQTT Consumer initialized")
    
    def on_message(self, topic: str, payload):
        """
        Callback for when a message is received.
        
        Args:
            topic: Topic the message was received on
            payload: Message payload (already parsed as JSON if applicable)
        """
        logger.info(f"Received message on topic '{topic}'")
        logger.debug(f"Payload: {payload}")
        
        # Process the message
        self.process_message(topic, payload)
    
    def process_message(self, topic: str, payload):
        """
        Process a received message.
        
        Args:
            topic: Topic the message was received on
            payload: Message payload
        """
        # Add your message processing logic here
        # Example: Extract sensor data
        if isinstance(payload, dict):
            if 'sensor_id' in payload and 'value' in payload:
                sensor_id = payload['sensor_id']
                value = payload['value']
                timestamp = payload.get('timestamp', 'N/A')
                logger.info(f"Sensor {sensor_id}: {value} at {timestamp}")
            else:
                logger.info(f"Received data: {payload}")
        else:
            logger.info(f"Received raw data: {payload}")
    
    def run(self):
        """Run the MQTT consumer agent."""
        try:
            # Connect to MQTT broker
            self.mqtt_client.connect()
            
            # Subscribe to topics
            for topic in self.topics:
                self.mqtt_client.subscribe(topic)
                logger.info(f"Subscribed to topic: {topic}")
            
            # Start the MQTT loop (blocking)
            logger.info("Starting MQTT consumer loop...")
            self.mqtt_client.start()
            
        except KeyboardInterrupt:
            logger.info("Shutting down MQTT Consumer...")
            self.mqtt_client.disconnect()
        except Exception as e:
            logger.error(f"Error in MQTT consumer: {e}")
            self.mqtt_client.disconnect()
            raise
    
    def stop(self):
        """Stop the MQTT consumer agent."""
        self.mqtt_client.disconnect()
        logger.info("MQTT Consumer stopped")


def main():
    """Main entry point."""
    consumer = MQTTDataConsumer()
    consumer.run()


if __name__ == "__main__":
    main()
