"""
Hybrid Consumer Template
Template combining MQTT and InfluxDB for comprehensive data consumption.
"""

import logging
from datetime import datetime, timedelta
from common import MQTTConsumer, InfluxConsumer, load_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HybridDataConsumer:
    """Hybrid data consumer using both MQTT and InfluxDB."""
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the hybrid consumer.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        
        # Initialize MQTT consumer
        mqtt_config = self.config.get('mqtt', {})
        self.mqtt_client = MQTTConsumer(
            broker=mqtt_config.get('broker', 'localhost'),
            port=mqtt_config.get('port', 1883),
            client_id=mqtt_config.get('client_id', 'hybrid_consumer'),
            username=mqtt_config.get('username'),
            password=mqtt_config.get('password')
        )
        self.mqtt_client.set_message_callback(self.on_mqtt_message)
        
        # Initialize InfluxDB consumer
        influx_config = self.config.get('influxdb', {})
        self.influx_client = InfluxConsumer(
            url=influx_config.get('url', 'http://localhost:8086'),
            token=influx_config.get('token'),
            org=influx_config.get('org'),
            bucket=influx_config.get('bucket')
        )
        
        # Get configuration
        self.topics = self.config.get('topics', ['sensors/#'])
        
        logger.info("Hybrid Consumer initialized")
    
    def on_mqtt_message(self, topic: str, payload):
        """
        Callback for MQTT messages.
        
        Args:
            topic: Topic the message was received on
            payload: Message payload
        """
        logger.info(f"Received MQTT message on '{topic}'")
        
        # Process real-time data from MQTT
        self.process_realtime_data(topic, payload)
        
        # Optionally query historical data from InfluxDB for context
        if isinstance(payload, dict) and 'sensor_id' in payload:
            self.query_sensor_history(payload['sensor_id'])
    
    def process_realtime_data(self, topic: str, payload):
        """
        Process real-time data from MQTT.
        
        Args:
            topic: Topic the message was received on
            payload: Message payload
        """
        logger.info(f"Processing real-time data: {payload}")
        
        # Add your real-time processing logic here
        # Example: Detect anomalies, trigger alerts, etc.
    
    def query_sensor_history(self, sensor_id: str):
        """
        Query historical data for a sensor from InfluxDB.
        
        Args:
            sensor_id: Sensor identifier
        """
        measurement = self.config.get('measurement', 'sensors')
        field = self.config.get('field', 'value')
        
        start_time = datetime.now() - timedelta(hours=1)
        
        try:
            results = self.influx_client.query_range(
                measurement=measurement,
                field=field,
                start=start_time,
                filters={'sensor_id': sensor_id}
            )
            
            if results:
                logger.info(f"Found {len(results)} historical records for sensor {sensor_id}")
                # Process historical data
                self.analyze_history(results)
            else:
                logger.info(f"No historical data found for sensor {sensor_id}")
                
        except Exception as e:
            logger.error(f"Error querying sensor history: {e}")
    
    def analyze_history(self, results):
        """
        Analyze historical data.
        
        Args:
            results: Query results from InfluxDB
        """
        if not results:
            return
        
        values = [r['value'] for r in results if r.get('value') is not None]
        
        if values:
            avg = sum(values) / len(values)
            logger.info(f"Historical average: {avg:.2f}")
            
            # Add more analysis logic here
    
    def run(self):
        """Run the hybrid consumer agent."""
        try:
            # Connect to MQTT broker
            self.mqtt_client.connect()
            
            # Subscribe to topics
            for topic in self.topics:
                self.mqtt_client.subscribe(topic)
                logger.info(f"Subscribed to topic: {topic}")
            
            # Start MQTT loop (this will run indefinitely)
            logger.info("Starting hybrid consumer...")
            self.mqtt_client.start()
            
        except KeyboardInterrupt:
            logger.info("Shutting down Hybrid Consumer...")
            self.stop()
        except Exception as e:
            logger.error(f"Error in hybrid consumer: {e}")
            self.stop()
            raise
    
    def stop(self):
        """Stop the hybrid consumer."""
        self.mqtt_client.disconnect()
        self.influx_client.close()
        logger.info("Hybrid Consumer stopped")


def main():
    """Main entry point."""
    consumer = HybridDataConsumer()
    consumer.run()


if __name__ == "__main__":
    main()
