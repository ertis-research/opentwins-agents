"""
TensorFlow Model Producer Template
Loads a trained TensorFlow model and publishes predictions to MQTT/InfluxDB.
"""

import logging
import time
import json
from datetime import datetime
import numpy as np
import tensorflow as tf
from pathlib import Path
from common import MQTTProducer, InfluxProducer, load_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TensorFlowProducer:
    """TensorFlow model-based data producer for online predictions."""
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the TensorFlow producer.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        
        # Load TensorFlow model
        model_path = self.config.get('model_path', 'model/saved_model')
        logger.info(f"Loading TensorFlow model from {model_path}")
        
        try:
            self.model = tf.keras.models.load_model(model_path)
            logger.info("Model loaded successfully")
            logger.info(f"Model input shape: {self.model.input_shape}")
            logger.info(f"Model output shape: {self.model.output_shape}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
        
        # Initialize MQTT client if enabled
        self.mqtt_client = None
        mqtt_config = self.config.get('mqtt', {})
        if mqtt_config.get('enabled', False):
            self.mqtt_client = MQTTProducer(
                broker=mqtt_config.get('broker', 'localhost'),
                port=mqtt_config.get('port', 1883),
                client_id=mqtt_config.get('client_id', 'tf_producer'),
                username=mqtt_config.get('username'),
                password=mqtt_config.get('password')
            )
            self.mqtt_client.connect()
            logger.info("MQTT client connected")
        
        # Initialize InfluxDB client if enabled
        self.influx_client = None
        influx_config = self.config.get('influxdb', {})
        if influx_config.get('enabled', False):
            self.influx_client = InfluxProducer(
                url=influx_config.get('url', 'http://localhost:8086'),
                token=influx_config.get('token'),
                org=influx_config.get('org'),
                bucket=influx_config.get('bucket')
            )
            logger.info("InfluxDB client initialized")
        
        # Model configuration
        self.input_shape = self.config.get('input_shape', list(self.model.input_shape[1:]))
        self.output_labels = self.config.get('output_labels', None)
        self.preprocessing = self.config.get('preprocessing', {})
        self.prediction_interval = self.config.get('prediction_interval', 1.0)
        
        self.running = False
        logger.info("TensorFlow Producer initialized")
    
    def preprocess_input(self, data):
        """
        Preprocess input data before prediction.
        
        Args:
            data: Input data (list or numpy array)
        
        Returns:
            Preprocessed numpy array ready for model
        """
        # Convert to numpy array
        if isinstance(data, list):
            data = np.array(data, dtype=np.float32)
        
        # Apply normalization if configured
        if self.preprocessing.get('normalize', False):
            mean = self.preprocessing.get('mean', 0.0)
            std = self.preprocessing.get('std', 1.0)
            data = (data - mean) / std
        
        # Apply min-max scaling if configured
        if self.preprocessing.get('scale', False):
            min_val = self.preprocessing.get('min', 0.0)
            max_val = self.preprocessing.get('max', 1.0)
            data = (data - min_val) / (max_val - min_val)
        
        # Reshape to model input shape if needed
        if len(data.shape) == 1:
            data = data.reshape(1, -1)
        
        return data
    
    def predict(self, input_data):
        """
        Make prediction using the loaded model.
        
        Args:
            input_data: Input data for prediction
        
        Returns:
            Dictionary containing prediction results
        """
        try:
            # Preprocess input
            processed_data = self.preprocess_input(input_data)
            
            # Make prediction
            prediction = self.model.predict(processed_data, verbose=0)
            
            # Build result dictionary
            result = {
                'timestamp': datetime.now().isoformat(),
                'raw_prediction': prediction.tolist()
            }
            
            # Handle classification output
            if self.output_labels and len(self.output_labels) > 0:
                predicted_class_idx = int(np.argmax(prediction, axis=-1)[0])
                result['predicted_class'] = self.output_labels[predicted_class_idx]
                result['predicted_class_idx'] = predicted_class_idx
                result['confidence'] = float(np.max(prediction))
                result['all_probabilities'] = {
                    label: float(prediction[0][i])
                    for i, label in enumerate(self.output_labels)
                }
            
            # Handle regression output (single value)
            elif prediction.shape[-1] == 1:
                result['predicted_value'] = float(prediction[0][0])
            
            # Handle multi-output regression
            else:
                result['predicted_values'] = prediction[0].tolist()
            
            logger.debug(f"Prediction: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return None
    
    def publish_prediction(self, prediction, metadata=None):
        """
        Publish prediction results to configured destinations.
        
        Args:
            prediction: Prediction results dictionary
            metadata: Additional metadata to include
        """
        if prediction is None:
            logger.warning("Skipping publication of null prediction")
            return
        
        # Add metadata if provided
        if metadata:
            prediction = {**prediction, **metadata}
        
        # Publish to MQTT
        if self.mqtt_client:
            topic = self.config.get('mqtt', {}).get('prediction_topic', 'ml/predictions')
            try:
                self.mqtt_client.publish_dict(topic, prediction)
                logger.info(f"Published prediction to MQTT topic: {topic}")
            except Exception as e:
                logger.error(f"Error publishing to MQTT: {e}")
        
        # Write to InfluxDB
        if self.influx_client:
            measurement = self.config.get('influxdb', {}).get('measurement', 'ml_predictions')
            
            try:
                # Prepare fields (numerical values)
                fields = {}
                if 'predicted_value' in prediction:
                    fields['predicted_value'] = prediction['predicted_value']
                if 'confidence' in prediction:
                    fields['confidence'] = prediction['confidence']
                if 'predicted_values' in prediction:
                    for i, val in enumerate(prediction['predicted_values']):
                        fields[f'output_{i}'] = val
                
                # Prepare tags (categorical values)
                tags = {}
                if 'predicted_class' in prediction:
                    tags['predicted_class'] = str(prediction['predicted_class'])
                if metadata:
                    for key, value in metadata.items():
                        if isinstance(value, (str, int, bool)):
                            tags[key] = str(value)
                
                if fields:
                    self.influx_client.write_point(
                        measurement=measurement,
                        fields=fields,
                        tags=tags,
                        timestamp=datetime.now()
                    )
                    logger.info(f"Wrote prediction to InfluxDB: {measurement}")
                
            except Exception as e:
                logger.error(f"Error writing to InfluxDB: {e}")
    
    def generate_sample_data(self):
        """
        Generate sample input data for testing.
        
        Returns:
            Random data matching model input shape
        """
        # Generate random data matching input shape
        shape = self.input_shape if isinstance(self.input_shape, list) else [self.input_shape]
        return np.random.randn(*shape).tolist()
    
    def run_batch_predictions(self, data_source):
        """
        Run predictions on a batch of data.
        
        Args:
            data_source: Iterable of input data
        """
        logger.info("Starting batch prediction mode")
        batch_interval = self.config.get('batch_interval', 0.5)
        
        for idx, input_data in enumerate(data_source):
            prediction = self.predict(input_data)
            metadata = {
                'batch_index': idx,
                'mode': 'batch'
            }
            self.publish_prediction(prediction, metadata)
            time.sleep(batch_interval)
        
        logger.info(f"Completed {idx + 1} batch predictions")
    
    def run_continuous(self):
        """Run continuous prediction loop with generated data."""
        self.running = True
        logger.info("Starting continuous prediction mode")
        logger.info(f"Prediction interval: {self.prediction_interval}s")
        
        try:
            iteration = 0
            while self.running:
                # Generate sample data (replace with actual data source in production)
                input_data = self.generate_sample_data()
                
                # Make prediction
                prediction = self.predict(input_data)
                
                # Add iteration metadata
                metadata = {
                    'iteration': iteration,
                    'mode': 'continuous'
                }
                
                # Publish results
                self.publish_prediction(prediction, metadata)
                
                # Wait before next prediction
                time.sleep(self.prediction_interval)
                iteration += 1
                
        except KeyboardInterrupt:
            logger.info("Stopping continuous prediction")
            self.stop()
    
    def stop(self):
        """Stop the producer and clean up resources."""
        self.running = False
        
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        
        if self.influx_client:
            self.influx_client.close()
        
        logger.info("TensorFlow Producer stopped")


def main():
    """Main entry point."""
    import sys
    
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
    
    producer = TensorFlowProducer(config_path)
    
    # Run in continuous mode (default)
    producer.run_continuous()
    
    # Alternative: Run with custom data source
    # data_source = [producer.generate_sample_data() for _ in range(10)]
    # producer.run_batch_predictions(data_source)


if __name__ == "__main__":
    main()
