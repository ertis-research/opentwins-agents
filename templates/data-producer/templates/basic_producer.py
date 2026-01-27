"""
Basic Data Producer Template
Simple template for producing data to various destinations.
"""

import logging
import time
from datetime import datetime
from common import load_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BasicProducer:
    """Basic data producer agent."""
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the basic producer.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.running = False
        self.interval = self.config.get('interval', 5)  # seconds
        logger.info("Basic Producer initialized")
    
    def generate_data(self):
        """
        Generate data to publish.
        
        Returns:
            Generated data
        """
        # Add your data generation logic here
        data = {
            'timestamp': datetime.now().isoformat(),
            'value': 42,
            'status': 'active'
        }
        return data
    
    def publish_data(self, data):
        """
        Publish generated data.
        
        Args:
            data: Data to publish
        """
        logger.info(f"Publishing data: {data}")
        # Add your publishing logic here
    
    def run(self):
        """Run the producer agent."""
        self.running = True
        logger.info("Starting Basic Producer...")
        
        try:
            while self.running:
                # Generate data
                data = self.generate_data()
                
                # Publish data
                self.publish_data(data)
                
                # Wait for next cycle
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            logger.info("Shutting down Basic Producer...")
            self.running = False
        except Exception as e:
            logger.error(f"Error in producer: {e}")
            raise
    
    def stop(self):
        """Stop the producer agent."""
        self.running = False
        logger.info("Basic Producer stopped")


def main():
    """Main entry point."""
    producer = BasicProducer()
    producer.run()


if __name__ == "__main__":
    main()
