"""
InfluxDB Producer Template
Template for producing data to InfluxDB.
"""

import logging
import time
from datetime import datetime
from common import InfluxProducer, load_config, generate_sensor_data

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InfluxDataProducer:
    """InfluxDB data producer agent."""
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the InfluxDB producer.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        
        # Initialize InfluxDB producer
        influx_config = self.config.get('influxdb', {})
        self.influx_client = InfluxProducer(
            url=influx_config.get('url', 'http://localhost:8086'),
            token=influx_config.get('token'),
            org=influx_config.get('org'),
            bucket=influx_config.get('bucket')
        )
        
        # Get configuration
        self.measurement = self.config.get('measurement', 'sensors')
        self.interval = self.config.get('interval', 5)  # seconds
        self.sensor_id = self.config.get('sensor_id', 'sensor_001')
        self.location = self.config.get('location', 'lab')
        
        self.running = False
        logger.info("InfluxDB Producer initialized")
    
    def generate_data(self):
        """
        Generate sensor data to write.
        
        Returns:
            Dictionary containing data point information
        """
        # Generate simulated sensor readings
        data = {
            'measurement': self.measurement,
            'tags': {
                'sensor_id': self.sensor_id,
                'location': self.location
            },
            'fields': {
                'temperature': generate_sensor_data('temperature', 22.0, 3.0),
                'humidity': generate_sensor_data('humidity', 60.0, 10.0),
                'pressure': generate_sensor_data('pressure', 1013.0, 5.0)
            },
            'timestamp': datetime.now()
        }
        return data
    
    def write_data(self, data):
        """
        Write data to InfluxDB.
        
        Args:
            data: Data point to write
        """
        try:
            self.influx_client.write_point(
                measurement=data['measurement'],
                fields=data['fields'],
                tags=data['tags'],
                timestamp=data['timestamp']
            )
            logger.info(f"Wrote data point: {data['fields']}")
        except Exception as e:
            logger.error(f"Error writing data: {e}")
    
    def run(self):
        """Run the InfluxDB producer agent."""
        self.running = True
        
        try:
            logger.info(f"Starting InfluxDB producer, writing to '{self.measurement}'")
            
            while self.running:
                # Generate data
                data = self.generate_data()
                
                # Write data
                self.write_data(data)
                
                # Wait for next cycle
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            logger.info("Shutting down InfluxDB Producer...")
            self.running = False
        except Exception as e:
            logger.error(f"Error in InfluxDB producer: {e}")
            raise
        finally:
            self.influx_client.close()
    
    def stop(self):
        """Stop the InfluxDB producer agent."""
        self.running = False
        self.influx_client.close()
        logger.info("InfluxDB Producer stopped")


def main():
    """Main entry point."""
    producer = InfluxDataProducer()
    producer.run()


if __name__ == "__main__":
    main()
