"""
MQTT Producer Template
Template for producing data to MQTT topics.
"""

import logging
import time
from datetime import datetime
from common import MQTTProducer, load_config, generate_sensor_data

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MQTTDataProducer:
    """MQTT data producer agent."""
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the MQTT producer.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        
        # Initialize MQTT producer
        mqtt_config = self.config.get('mqtt', {})
        self.mqtt_client = MQTTProducer(
            broker=mqtt_config.get('broker', 'localhost'),
            port=mqtt_config.get('port', 1883),
            client_id=mqtt_config.get('client_id', 'mqtt_producer'),
            username=mqtt_config.get('username'),
            password=mqtt_config.get('password')
        )
        
        # Get configuration
        self.topic = self.config.get('topic', 'sensors/data')
        self.interval = self.config.get('interval', 5)  # seconds
        self.sensor_id = self.config.get('sensor_id', 'sensor_001')
        
        self.running = False
        logger.info("MQTT Producer initialized")
    
    def generate_data(self):
        """
        Generate sensor data to publish.
        
        Returns:
            Dictionary containing sensor data
        """
        # Generate simulated sensor readings
        data = {
            'sensor_id': self.sensor_id,
            'timestamp': datetime.now().isoformat(),
            'temperature': generate_sensor_data('temperature', 22.0, 3.0),
            'humidity': generate_sensor_data('humidity', 60.0, 10.0),
            'pressure': generate_sensor_data('pressure', 1013.0, 5.0)
        }
        return data
    
    def publish_data(self, data):
        """
        Publish data to MQTT topic.
        
        Args:
            data: Data to publish
        """
        try:
            self.mqtt_client.publish_dict(self.topic, data)
            logger.info(f"Published to '{self.topic}': {data}")
        except Exception as e:
            logger.error(f"Error publishing data: {e}")
    
    def run(self):
        """Run the MQTT producer agent."""
        self.running = True
        
        try:
            # Connect to MQTT broker
            self.mqtt_client.connect()
            logger.info(f"Connected to MQTT broker, publishing to '{self.topic}'")
            
            while self.running:
                # Generate data
                data = self.generate_data()
                
                # Publish data
                self.publish_data(data)
                
                # Wait for next cycle
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            logger.info("Shutting down MQTT Producer...")
            self.running = False
        except Exception as e:
            logger.error(f"Error in MQTT producer: {e}")
            raise
        finally:
            self.mqtt_client.disconnect()
    
    def stop(self):
        """Stop the MQTT producer agent."""
        self.running = False
        self.mqtt_client.disconnect()
        logger.info("MQTT Producer stopped")


def main():
    """Main entry point."""
    producer = MQTTDataProducer()
    producer.run()


if __name__ == "__main__":
    main()
