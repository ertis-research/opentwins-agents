"""
InfluxDB Client Module for Data Consumer
Provides utilities for reading data from InfluxDB.
"""

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.query_api import QueryApi
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InfluxConsumer:
    """InfluxDB Consumer client for reading time-series data."""
    
    def __init__(self, url: str, token: str, org: str, bucket: Optional[str] = None,
                 timeout: int = 30000):
        """
        Initialize InfluxDB Consumer.
        
        Args:
            url: InfluxDB server URL
            token: Authentication token
            org: Organization name
            bucket: Default bucket name (optional)
            timeout: Query timeout in milliseconds
        """
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.timeout = timeout
        
        self.client = InfluxDBClient(url=url, token=token, org=org, timeout=timeout)
        self.query_api: QueryApi = self.client.query_api()
        
        logger.info(f"Initialized InfluxDB consumer for {url}")
    
    def query(self, flux_query: str) -> List[Dict[str, Any]]:
        """
        Execute a Flux query and return results as a list of dictionaries.
        
        Args:
            flux_query: Flux query string
        
        Returns:
            List of dictionaries containing query results
        """
        try:
            logger.debug(f"Executing query: {flux_query}")
            tables = self.query_api.query(flux_query, org=self.org)
            
            results = []
            for table in tables:
                for record in table.records:
                    results.append({
                        'time': record.get_time(),
                        'measurement': record.get_measurement(),
                        'field': record.get_field(),
                        'value': record.get_value(),
                        **record.values
                    })
            
            logger.info(f"Query returned {len(results)} records")
            return results
        
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    def query_range(self, measurement: str, field: str, 
                   start: datetime, stop: Optional[datetime] = None,
                   bucket: Optional[str] = None,
                   filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Query data for a specific measurement and field within a time range.
        
        Args:
            measurement: Measurement name
            field: Field name
            start: Start time
            stop: Stop time (default: now)
            bucket: Bucket name (uses default if not specified)
            filters: Additional tag filters (e.g., {'sensor': 'temp_01'})
        
        Returns:
            List of dictionaries containing query results
        """
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket must be specified either in constructor or query_range")
        
        stop = stop or datetime.now()
        
        # Build Flux query
        query = f'''
        from(bucket: "{bucket}")
          |> range(start: {start.isoformat()}Z, stop: {stop.isoformat()}Z)
          |> filter(fn: (r) => r["_measurement"] == "{measurement}")
          |> filter(fn: (r) => r["_field"] == "{field}")
        '''
        
        # Add tag filters if provided
        if filters:
            for tag, value in filters.items():
                query += f'\n  |> filter(fn: (r) => r["{tag}"] == "{value}")'
        
        return self.query(query)
    
    def query_last(self, measurement: str, field: str,
                  bucket: Optional[str] = None,
                  filters: Optional[Dict[str, str]] = None,
                  limit: int = 1) -> List[Dict[str, Any]]:
        """
        Query the last N records for a specific measurement and field.
        
        Args:
            measurement: Measurement name
            field: Field name
            bucket: Bucket name (uses default if not specified)
            filters: Additional tag filters
            limit: Number of records to return
        
        Returns:
            List of dictionaries containing the most recent records
        """
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket must be specified")
        
        query = f'''
        from(bucket: "{bucket}")
          |> range(start: -7d)
          |> filter(fn: (r) => r["_measurement"] == "{measurement}")
          |> filter(fn: (r) => r["_field"] == "{field}")
        '''
        
        if filters:
            for tag, value in filters.items():
                query += f'\n  |> filter(fn: (r) => r["{tag}"] == "{value}")'
        
        query += f'\n  |> sort(columns: ["_time"], desc: true)'
        query += f'\n  |> limit(n: {limit})'
        
        return self.query(query)
    
    def query_aggregated(self, measurement: str, field: str,
                        aggregation: str, window: str,
                        start: datetime, stop: Optional[datetime] = None,
                        bucket: Optional[str] = None,
                        filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Query aggregated data (mean, sum, min, max, etc.) over time windows.
        
        Args:
            measurement: Measurement name
            field: Field name
            aggregation: Aggregation function (mean, sum, min, max, count, etc.)
            window: Time window for aggregation (e.g., "1h", "5m", "1d")
            start: Start time
            stop: Stop time (default: now)
            bucket: Bucket name (uses default if not specified)
            filters: Additional tag filters
        
        Returns:
            List of dictionaries containing aggregated results
        """
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket must be specified")
        
        stop = stop or datetime.now()
        
        query = f'''
        from(bucket: "{bucket}")
          |> range(start: {start.isoformat()}Z, stop: {stop.isoformat()}Z)
          |> filter(fn: (r) => r["_measurement"] == "{measurement}")
          |> filter(fn: (r) => r["_field"] == "{field}")
        '''
        
        if filters:
            for tag, value in filters.items():
                query += f'\n  |> filter(fn: (r) => r["{tag}"] == "{value}")'
        
        query += f'\n  |> aggregateWindow(every: {window}, fn: {aggregation}, createEmpty: false)'
        
        return self.query(query)
    
    def close(self):
        """Close the InfluxDB client connection."""
        self.client.close()
        logger.info("InfluxDB client connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def create_influx_consumer(config: Dict[str, Any]) -> InfluxConsumer:
    """
    Factory function to create an InfluxDB consumer from a configuration dictionary.
    
    Args:
        config: Dictionary containing InfluxDB configuration
               Expected keys: url, token, org, bucket, timeout
    
    Returns:
        Configured InfluxConsumer instance
    """
    return InfluxConsumer(
        url=config.get('url'),
        token=config.get('token'),
        org=config.get('org'),
        bucket=config.get('bucket'),
        timeout=config.get('timeout', 30000)
    )
