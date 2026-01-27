"""
Common Utilities for Data Producer
Provides general-purpose helper functions.
"""

import json
import logging
import os
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import time
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file
    
    Returns:
        Dictionary containing configuration
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        raise


def save_config(config: Dict[str, Any], config_path: str):
    """
    Save configuration to a JSON file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save the configuration file
    """
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Configuration saved to {config_path}")
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        raise


def get_env_variable(var_name: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get an environment variable with optional default value.
    
    Args:
        var_name: Name of the environment variable
        default: Default value if variable is not set
        required: If True, raises ValueError when variable is not found
    
    Returns:
        Environment variable value or default
    """
    value = os.getenv(var_name, default)
    
    if required and value is None:
        raise ValueError(f"Required environment variable '{var_name}' is not set")
    
    return value


def timestamp_to_datetime(timestamp: int, unit: str = 'ms') -> datetime:
    """
    Convert a timestamp to a datetime object.
    
    Args:
        timestamp: Unix timestamp
        unit: Time unit ('s' for seconds, 'ms' for milliseconds, 'us' for microseconds)
    
    Returns:
        datetime object
    """
    if unit == 's':
        return datetime.fromtimestamp(timestamp)
    elif unit == 'ms':
        return datetime.fromtimestamp(timestamp / 1000.0)
    elif unit == 'us':
        return datetime.fromtimestamp(timestamp / 1000000.0)
    else:
        raise ValueError(f"Invalid time unit: {unit}")


def datetime_to_timestamp(dt: datetime, unit: str = 'ms') -> int:
    """
    Convert a datetime object to a timestamp.
    
    Args:
        dt: datetime object
        unit: Time unit ('s' for seconds, 'ms' for milliseconds, 'us' for microseconds)
    
    Returns:
        Unix timestamp
    """
    timestamp = dt.timestamp()
    
    if unit == 's':
        return int(timestamp)
    elif unit == 'ms':
        return int(timestamp * 1000)
    elif unit == 'us':
        return int(timestamp * 1000000)
    else:
        raise ValueError(f"Invalid time unit: {unit}")


def retry_with_backoff(func, max_retries: int = 3, initial_delay: float = 1.0, 
                       backoff_factor: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Retry a function with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch
    
    Returns:
        Function result if successful
    """
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            return func()
        except exceptions as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed after {max_retries} attempts: {e}")
                raise
            
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= backoff_factor


def generate_sensor_data(sensor_type: str, base_value: float = 20.0, 
                        variance: float = 5.0) -> float:
    """
    Generate simulated sensor data with random variance.
    
    Args:
        sensor_type: Type of sensor (temperature, humidity, pressure, etc.)
        base_value: Base value for the sensor reading
        variance: Maximum variance from base value
    
    Returns:
        Simulated sensor reading
    """
    value = base_value + random.uniform(-variance, variance)
    
    # Apply sensor-specific constraints
    if sensor_type == 'humidity':
        value = max(0, min(100, value))  # 0-100%
    elif sensor_type == 'temperature':
        value = max(-50, min(100, value))  # -50 to 100°C
    elif sensor_type == 'pressure':
        value = max(900, min(1100, value))  # 900-1100 hPa
    
    return round(value, 2)


def generate_batch_data(count: int, measurement: str, fields: Dict[str, tuple],
                       tags: Optional[Dict[str, str]] = None,
                       start_time: Optional[datetime] = None,
                       interval_seconds: int = 1) -> list:
    """
    Generate a batch of simulated data points.
    
    Args:
        count: Number of data points to generate
        measurement: Measurement name
        fields: Dictionary of field_name: (sensor_type, base_value, variance) tuples
        tags: Dictionary of tag key-value pairs
        start_time: Start timestamp (default: now)
        interval_seconds: Time interval between points in seconds
    
    Returns:
        List of data point dictionaries
    """
    start_time = start_time or datetime.now()
    tags = tags or {}
    
    data_points = []
    
    for i in range(count):
        timestamp = start_time + timedelta(seconds=i * interval_seconds)
        
        # Generate field values
        field_values = {}
        for field_name, (sensor_type, base_value, variance) in fields.items():
            field_values[field_name] = generate_sensor_data(sensor_type, base_value, variance)
        
        data_points.append({
            'measurement': measurement,
            'tags': tags.copy(),
            'fields': field_values,
            'timestamp': timestamp
        })
    
    return data_points


class DataGenerator:
    """Continuous data generator for simulation purposes."""
    
    def __init__(self, measurement: str, fields: Dict[str, tuple],
                 tags: Optional[Dict[str, str]] = None,
                 interval_seconds: float = 1.0):
        """
        Initialize data generator.
        
        Args:
            measurement: Measurement name
            fields: Dictionary of field_name: (sensor_type, base_value, variance) tuples
            tags: Dictionary of tag key-value pairs
            interval_seconds: Time interval between data points
        """
        self.measurement = measurement
        self.fields = fields
        self.tags = tags or {}
        self.interval_seconds = interval_seconds
        self.running = False
    
    def generate_point(self) -> Dict[str, Any]:
        """Generate a single data point."""
        field_values = {}
        for field_name, (sensor_type, base_value, variance) in self.fields.items():
            field_values[field_name] = generate_sensor_data(sensor_type, base_value, variance)
        
        return {
            'measurement': self.measurement,
            'tags': self.tags.copy(),
            'fields': field_values,
            'timestamp': datetime.now()
        }
    
    def start(self, callback):
        """
        Start generating data continuously.
        
        Args:
            callback: Function to call with each generated data point
        """
        self.running = True
        logger.info(f"Starting data generator for '{self.measurement}'")
        
        while self.running:
            point = self.generate_point()
            callback(point)
            time.sleep(self.interval_seconds)
    
    def stop(self):
        """Stop the data generator."""
        self.running = False
        logger.info("Data generator stopped")


class RateLimiter:
    """Simple rate limiter to control operation frequency."""
    
    def __init__(self, max_calls: int, time_window: float):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed in the time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def allow(self) -> bool:
        """
        Check if a new call is allowed.
        
        Returns:
            True if the call is allowed, False otherwise
        """
        now = time.time()
        
        # Remove calls outside the time window
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < self.time_window]
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        
        return False
    
    def wait_if_needed(self):
        """Wait until a call is allowed (blocking)."""
        while not self.allow():
            time.sleep(0.1)
