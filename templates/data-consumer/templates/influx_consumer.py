"""
InfluxDB Consumer Template
Template for consuming and analyzing data from InfluxDB.
"""

import logging
from datetime import datetime, timedelta
from common import InfluxConsumer, load_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InfluxDataConsumer:
    """InfluxDB data consumer agent."""
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the InfluxDB consumer.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        
        # Initialize InfluxDB consumer
        influx_config = self.config.get('influxdb', {})
        self.influx_client = InfluxConsumer(
            url=influx_config.get('url', 'http://localhost:8086'),
            token=influx_config.get('token'),
            org=influx_config.get('org'),
            bucket=influx_config.get('bucket')
        )
        
        logger.info("InfluxDB Consumer initialized")
    
    def query_recent_data(self, hours: int = 1):
        """
        Query recent data from InfluxDB.
        
        Args:
            hours: Number of hours to look back
        """
        measurement = self.config.get('measurement', 'sensors')
        field = self.config.get('field', 'value')
        
        start_time = datetime.now() - timedelta(hours=hours)
        
        logger.info(f"Querying data for the last {hours} hour(s)")
        results = self.influx_client.query_range(
            measurement=measurement,
            field=field,
            start=start_time
        )
        
        logger.info(f"Retrieved {len(results)} data points")
        self.process_results(results)
    
    def query_last_values(self, limit: int = 10):
        """
        Query the last N values from InfluxDB.
        
        Args:
            limit: Number of values to retrieve
        """
        measurement = self.config.get('measurement', 'sensors')
        field = self.config.get('field', 'value')
        
        logger.info(f"Querying last {limit} values")
        results = self.influx_client.query_last(
            measurement=measurement,
            field=field,
            limit=limit
        )
        
        logger.info(f"Retrieved {len(results)} data points")
        self.process_results(results)
    
    def query_aggregated_data(self, hours: int = 24, window: str = '1h'):
        """
        Query aggregated data from InfluxDB.
        
        Args:
            hours: Number of hours to look back
            window: Aggregation window (e.g., '1h', '5m')
        """
        measurement = self.config.get('measurement', 'sensors')
        field = self.config.get('field', 'value')
        
        start_time = datetime.now() - timedelta(hours=hours)
        
        logger.info(f"Querying aggregated data (window: {window})")
        results = self.influx_client.query_aggregated(
            measurement=measurement,
            field=field,
            aggregation='mean',
            window=window,
            start=start_time
        )
        
        logger.info(f"Retrieved {len(results)} aggregated data points")
        self.process_results(results)
    
    def process_results(self, results):
        """
        Process query results.
        
        Args:
            results: List of query results
        """
        if not results:
            logger.warning("No results to process")
            return
        
        # Add your data processing logic here
        # Example: Print statistics
        values = [r['value'] for r in results if r.get('value') is not None]
        
        if values:
            avg_value = sum(values) / len(values)
            min_value = min(values)
            max_value = max(values)
            
            logger.info(f"Statistics:")
            logger.info(f"  Count: {len(values)}")
            logger.info(f"  Average: {avg_value:.2f}")
            logger.info(f"  Min: {min_value:.2f}")
            logger.info(f"  Max: {max_value:.2f}")
        
        # Print first few results
        logger.info(f"Sample data (first 5):")
        for result in results[:5]:
            logger.info(f"  {result}")
    
    def run(self):
        """Run the InfluxDB consumer agent."""
        try:
            # Example: Query recent data
            self.query_recent_data(hours=1)
            
            # Example: Query last values
            # self.query_last_values(limit=10)
            
            # Example: Query aggregated data
            # self.query_aggregated_data(hours=24, window='1h')
            
        except Exception as e:
            logger.error(f"Error in InfluxDB consumer: {e}")
            raise
        finally:
            self.influx_client.close()
    
    def close(self):
        """Close the InfluxDB consumer."""
        self.influx_client.close()
        logger.info("InfluxDB Consumer closed")


def main():
    """Main entry point."""
    consumer = InfluxDataConsumer()
    consumer.run()


if __name__ == "__main__":
    main()
