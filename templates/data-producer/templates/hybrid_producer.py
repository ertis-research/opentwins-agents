"""
Hybrid Producer Template
Template for producing data to both MQTT and InfluxDB simultaneously.
"""

import logging
import time
from datetime import datetime
from common import MQTTProducer, InfluxProducer, load_config, generate_sensor_data

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HybridDataProducer:
    """Hybrid data producer publishing to both MQTT and InfluxDB."""
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the hybrid producer.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        
        # Initialize MQTT producer
        mqtt_config = self.config.get('mqtt', {})
        self.mqtt_client = MQTTProducer(
            broker=mqtt_config.get('broker', 'localhost'),
            port=mqtt_config.get('port', 1883),
            client_id=mqtt_config.get('client_id', 'hybrid_producer'),
            username=mqtt_config.get('username'),
            password=mqtt_config.get('password')
        )
        
        # Initialize InfluxDB producer
        influx_config = self.config.get('influxdb', {})
        self.influx_client = InfluxProducer(
            url=influx_config.get('url', 'http://localhost:8086'),
            token=influx_config.get('token'),
            org=influx_config.get('org'),
            bucket=influx_config.get('bucket')
        )
        
        # Get configuration
        self.mqtt_topic = self.config.get('mqtt_topic', 'sensors/data')
        self.measurement = self.config.get('measurement', 'sensors')
        self.interval = self.config.get('interval', 5)  # seconds
        self.sensor_id = self.config.get('sensor_id', 'sensor_001')
        self.location = self.config.get('location', 'lab')
        
        self.running = False
        logger.info("Hybrid Producer initialized")
    
    def generate_data(self):
        """
        Generate sensor data.
        
        Returns:
            Tuple of (mqtt_data, influx_data)
        """
        timestamp = datetime.now()
        
        # Generate sensor readings
        temperature = generate_sensor_data('temperature', 22.0, 3.0)
        humidity = generate_sensor_data('humidity', 60.0, 10.0)
        pressure = generate_sensor_data('pressure', 1013.0, 5.0)
        
        # Data for MQTT (JSON format)
        mqtt_data = {
            'sensor_id': self.sensor_id,
            'location': self.location,
            'timestamp': timestamp.isoformat(),
            'temperature': temperature,
            'humidity': humidity,
            'pressure': pressure
        }
        
        # Data for InfluxDB (point format)
        influx_data = {
            'measurement': self.measurement,
            'tags': {
                'sensor_id': self.sensor_id,
                'location': self.location
            },
            'fields': {
                'temperature': temperature,
                'humidity': humidity,
                'pressure': pressure
            },
            'timestamp': timestamp
        }
        
        return mqtt_data, influx_data
    
    def publish_data(self, mqtt_data, influx_data):
        """
        Publish data to both MQTT and InfluxDB.
        
        Args:
            mqtt_data: Data for MQTT
            influx_data: Data for InfluxDB
        """
        # Publish to MQTT (for real-time subscribers)
        try:
            self.mqtt_client.publish_dict(self.mqtt_topic, mqtt_data)
            logger.info(f"Published to MQTT topic '{self.mqtt_topic}'")
        except Exception as e:
            logger.error(f"Error publishing to MQTT: {e}")
        
        # Write to InfluxDB (for historical storage)
        try:
            self.influx_client.write_point(
                measurement=influx_data['measurement'],
                fields=influx_data['fields'],
                tags=influx_data['tags'],
                timestamp=influx_data['timestamp']
            )
            logger.info(f"Wrote to InfluxDB measurement '{self.measurement}'")
        except Exception as e:
            logger.error(f"Error writing to InfluxDB: {e}")
    
    def run(self):
        """Run the hybrid producer agent."""
        self.running = True
        
        try:
            # Connect to MQTT broker
            self.mqtt_client.connect()
            logger.info("Connected to MQTT broker")
            
            logger.info("Starting hybrid producer...")
            logger.info(f"Publishing to MQTT topic: {self.mqtt_topic}")
            logger.info(f"Writing to InfluxDB measurement: {self.measurement}")
            
            while self.running:
                # Generate data
                mqtt_data, influx_data = self.generate_data()
                
                # Publish to both destinations
                self.publish_data(mqtt_data, influx_data)
                
                logger.info(f"Data: temp={mqtt_data['temperature']:.2f}°C, "
                          f"humidity={mqtt_data['humidity']:.2f}%, "
                          f"pressure={mqtt_data['pressure']:.2f}hPa")
                
                # Wait for next cycle
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            logger.info("Shutting down Hybrid Producer...")
            self.running = False
        except Exception as e:
            logger.error(f"Error in hybrid producer: {e}")
            raise
        finally:
            self.mqtt_client.disconnect()
            self.influx_client.close()
    
    def stop(self):
        """Stop the hybrid producer agent."""
        self.running = False
        self.mqtt_client.disconnect()
        self.influx_client.close()
        logger.info("Hybrid Producer stopped")


def main():
    """Main entry point."""
    producer = HybridDataProducer()
    producer.run()


if __name__ == "__main__":
    main()
