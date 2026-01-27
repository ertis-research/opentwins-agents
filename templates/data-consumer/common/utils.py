"""
Common Utilities for Data Consumer
Provides general-purpose helper functions.
"""

import json
import logging
import os
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import time

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


def validate_data(data: Dict[str, Any], required_fields: list) -> bool:
    """
    Validate that a data dictionary contains all required fields.
    
    Args:
        data: Data dictionary to validate
        required_fields: List of required field names
    
    Returns:
        True if all required fields are present, False otherwise
    """
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        logger.warning(f"Missing required fields: {missing_fields}")
        return False
    
    return True


def format_size(size_bytes: int) -> str:
    """
    Format a size in bytes to a human-readable string.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def parse_time_range(time_str: str) -> timedelta:
    """
    Parse a time range string to a timedelta object.
    
    Args:
        time_str: Time range string (e.g., "1h", "30m", "7d")
    
    Returns:
        timedelta object
    """
    units = {
        's': 'seconds',
        'm': 'minutes',
        'h': 'hours',
        'd': 'days',
        'w': 'weeks'
    }
    
    if len(time_str) < 2:
        raise ValueError(f"Invalid time range format: {time_str}")
    
    value = int(time_str[:-1])
    unit = time_str[-1]
    
    if unit not in units:
        raise ValueError(f"Invalid time unit: {unit}")
    
    return timedelta(**{units[unit]: value})


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
