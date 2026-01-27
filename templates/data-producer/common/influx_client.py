"""
InfluxDB Client Module for Data Producer
Provides utilities for writing data to InfluxDB.
"""

from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS, WriteApi
from typing import List, Dict, Any, Optional, Union
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InfluxProducer:
    """InfluxDB Producer client for writing time-series data."""
    
    def __init__(self, url: str, token: str, org: str, bucket: str,
                 batch_size: int = 1000, flush_interval: int = 10000,
                 timeout: int = 30000):
        """
        Initialize InfluxDB Producer.
        
        Args:
            url: InfluxDB server URL
            token: Authentication token
            org: Organization name
            bucket: Bucket name for writing data
            batch_size: Number of points to write in a batch
            flush_interval: Time in milliseconds to flush data
            timeout: Write timeout in milliseconds
        """
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.timeout = timeout
        
        self.client = InfluxDBClient(url=url, token=token, org=org, timeout=timeout)
        
        # Create write API with batching
        self.write_api: WriteApi = self.client.write_api(
            write_options=WriteOptions(
                batch_size=batch_size,
                flush_interval=flush_interval
            )
        )
        
        logger.info(f"Initialized InfluxDB producer for {url}, bucket: {bucket}")
    
    def write_point(self, measurement: str, fields: Dict[str, Any], 
                   tags: Optional[Dict[str, str]] = None,
                   timestamp: Optional[datetime] = None,
                   bucket: Optional[str] = None):
        """
        Write a single data point to InfluxDB.
        
        Args:
            measurement: Measurement name
            fields: Dictionary of field key-value pairs
            tags: Dictionary of tag key-value pairs (optional)
            timestamp: Point timestamp (default: current time)
            bucket: Bucket name (uses default if not specified)
        """
        bucket = bucket or self.bucket
        
        # Create point
        point = Point(measurement)
        
        # Add tags
        if tags:
            for tag_key, tag_value in tags.items():
                point = point.tag(tag_key, tag_value)
        
        # Add fields
        for field_key, field_value in fields.items():
            point = point.field(field_key, field_value)
        
        # Add timestamp if provided
        if timestamp:
            point = point.time(timestamp)
        
        try:
            self.write_api.write(bucket=bucket, org=self.org, record=point)
            logger.debug(f"Wrote point to measurement '{measurement}'")
        except Exception as e:
            logger.error(f"Error writing point: {e}")
            raise
    
    def write_points(self, points: List[Dict[str, Any]], bucket: Optional[str] = None):
        """
        Write multiple data points to InfluxDB.
        
        Args:
            points: List of point dictionaries, each containing:
                   - measurement: Measurement name
                   - fields: Dictionary of field key-value pairs
                   - tags: Dictionary of tag key-value pairs (optional)
                   - timestamp: Point timestamp (optional)
            bucket: Bucket name (uses default if not specified)
        """
        bucket = bucket or self.bucket
        
        point_objects = []
        for point_data in points:
            point = Point(point_data['measurement'])
            
            # Add tags
            if 'tags' in point_data and point_data['tags']:
                for tag_key, tag_value in point_data['tags'].items():
                    point = point.tag(tag_key, tag_value)
            
            # Add fields
            for field_key, field_value in point_data['fields'].items():
                point = point.field(field_key, field_value)
            
            # Add timestamp if provided
            if 'timestamp' in point_data and point_data['timestamp']:
                point = point.time(point_data['timestamp'])
            
            point_objects.append(point)
        
        try:
            self.write_api.write(bucket=bucket, org=self.org, record=point_objects)
            logger.info(f"Wrote {len(point_objects)} points to bucket '{bucket}'")
        except Exception as e:
            logger.error(f"Error writing points: {e}")
            raise
    
    def write_from_dict(self, data: Dict[str, Any], measurement: str,
                       tag_keys: Optional[List[str]] = None,
                       timestamp_key: str = 'timestamp',
                       bucket: Optional[str] = None):
        """
        Write data from a dictionary, automatically separating tags and fields.
        
        Args:
            data: Dictionary containing the data
            measurement: Measurement name
            tag_keys: List of keys to use as tags (others will be fields)
            timestamp_key: Key to use for timestamp (optional)
            bucket: Bucket name (uses default if not specified)
        """
        bucket = bucket or self.bucket
        tag_keys = tag_keys or []
        
        # Separate tags and fields
        tags = {key: str(data[key]) for key in tag_keys if key in data}
        
        # Get timestamp if present
        timestamp = None
        if timestamp_key in data:
            timestamp = data[timestamp_key]
            if isinstance(timestamp, int):
                # Assume milliseconds
                timestamp = datetime.fromtimestamp(timestamp / 1000.0)
        
        # Remaining keys are fields
        excluded_keys = set(tag_keys) | {timestamp_key}
        fields = {key: value for key, value in data.items() 
                 if key not in excluded_keys}
        
        if not fields:
            logger.warning("No fields to write")
            return
        
        self.write_point(measurement, fields, tags, timestamp, bucket)
    
    def write_dataframe(self, df, measurement: str, 
                       tag_columns: Optional[List[str]] = None,
                       timestamp_column: str = 'timestamp',
                       bucket: Optional[str] = None):
        """
        Write a pandas DataFrame to InfluxDB.
        
        Args:
            df: pandas DataFrame
            measurement: Measurement name
            tag_columns: List of columns to use as tags
            timestamp_column: Column to use for timestamp
            bucket: Bucket name (uses default if not specified)
        """
        bucket = bucket or self.bucket
        tag_columns = tag_columns or []
        
        try:
            from influxdb_client.client.write_api import SYNCHRONOUS
            
            # Convert DataFrame to line protocol
            self.write_api.write(
                bucket=bucket,
                org=self.org,
                record=df,
                data_frame_measurement_name=measurement,
                data_frame_tag_columns=tag_columns,
                data_frame_timestamp_column=timestamp_column
            )
            
            logger.info(f"Wrote {len(df)} rows from DataFrame to measurement '{measurement}'")
        except Exception as e:
            logger.error(f"Error writing DataFrame: {e}")
            raise
    
    def flush(self):
        """Flush any pending writes."""
        try:
            self.write_api.flush()
            logger.debug("Flushed pending writes")
        except Exception as e:
            logger.error(f"Error flushing writes: {e}")
            raise
    
    def close(self):
        """Close the InfluxDB client connection."""
        self.write_api.close()
        self.client.close()
        logger.info("InfluxDB producer connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def create_influx_producer(config: Dict[str, Any]) -> InfluxProducer:
    """
    Factory function to create an InfluxDB producer from a configuration dictionary.
    
    Args:
        config: Dictionary containing InfluxDB configuration
               Expected keys: url, token, org, bucket, batch_size, flush_interval, timeout
    
    Returns:
        Configured InfluxProducer instance
    """
    return InfluxProducer(
        url=config.get('url'),
        token=config.get('token'),
        org=config.get('org'),
        bucket=config.get('bucket'),
        batch_size=config.get('batch_size', 1000),
        flush_interval=config.get('flush_interval', 10000),
        timeout=config.get('timeout', 30000)
    )
