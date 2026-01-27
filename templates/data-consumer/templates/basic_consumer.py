"""
Basic Data Consumer Template
Simple template for consuming data from various sources.
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


class BasicConsumer:
    """Basic data consumer agent."""
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the basic consumer.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.running = False
        logger.info("Basic Consumer initialized")
    
    def process_data(self, data):
        """
        Process received data.
        
        Args:
            data: Data to process
        """
        logger.info(f"Processing data: {data}")
        # Add your data processing logic here
    
    def run(self):
        """Run the consumer agent."""
        self.running = True
        logger.info("Starting Basic Consumer...")
        
        try:
            while self.running:
                # Implement your data consumption logic here
                logger.info("Consumer is running...")
                time.sleep(5)
                
        except KeyboardInterrupt:
            logger.info("Shutting down Basic Consumer...")
            self.running = False
        except Exception as e:
            logger.error(f"Error in consumer: {e}")
            raise
    
    def stop(self):
        """Stop the consumer agent."""
        self.running = False
        logger.info("Basic Consumer stopped")


def main():
    """Main entry point."""
    consumer = BasicConsumer()
    consumer.run()


if __name__ == "__main__":
    main()
