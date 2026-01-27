# Data Producer Templates

This folder contains templates and utilities for creating data producer agents.

## Structure

```
data-producer/
├── common/                 # Shared utilities and clients
│   ├── __init__.py        # Module exports
│   ├── mqtt_client.py     # MQTT producer client
│   ├── influx_client.py   # InfluxDB producer client
│   └── utils.py           # Common helper functions
├── templates/             # Agent templates
│   ├── basic_producer.py  # Basic producer template
│   ├── mqtt_producer.py   # MQTT-specific producer
│   ├── influx_producer.py # InfluxDB-specific producer
│   └── hybrid_producer.py # Combined MQTT + InfluxDB producer
└── requirements.txt       # Python dependencies
```

## Common Utilities

### MQTT Client (`common/mqtt_client.py`)
- **MQTTProducer**: Publish messages to MQTT topics
- Features:
  - Automatic JSON serialization
  - Batch publishing
  - Support for TLS/SSL
  - Authentication support
  - QoS levels and retain flag

### InfluxDB Client (`common/influx_client.py`)
- **InfluxProducer**: Write data points to InfluxDB
- Features:
  - Batch writing with configurable size
  - Automatic flushing
  - Support for tags and fields
  - DataFrame integration
  - Timestamp handling

### Utilities (`common/utils.py`)
- Configuration loading/saving
- Environment variable handling
- Timestamp conversion utilities
- Sensor data generation for testing
- Batch data generation
- Rate limiting

## Templates

### Basic Producer (`templates/basic_producer.py`)
Simple template for creating custom producer agents.

```python
from templates.basic_producer import BasicProducer

producer = BasicProducer('config.json')
producer.run()
```

### MQTT Producer (`templates/mqtt_producer.py`)
Publish data to MQTT topics at regular intervals.

**Configuration example:**
```json
{
  "mqtt": {
    "broker": "localhost",
    "port": 1883,
    "client_id": "my_producer",
    "username": "user",
    "password": "pass"
  },
  "topic": "sensors/data",
  "sensor_id": "sensor_001",
  "interval": 5
}
```

**Usage:**
```python
from templates.mqtt_producer import MQTTDataProducer

producer = MQTTDataProducer('config.json')
producer.run()
```

### InfluxDB Producer (`templates/influx_producer.py`)
Write time-series data to InfluxDB.

**Configuration example:**
```json
{
  "influxdb": {
    "url": "http://localhost:8086",
    "token": "your-token",
    "org": "your-org",
    "bucket": "your-bucket"
  },
  "measurement": "sensors",
  "sensor_id": "sensor_001",
  "location": "lab",
  "interval": 5
}
```

**Usage:**
```python
from templates.influx_producer import InfluxDataProducer

producer = InfluxDataProducer('config.json')
producer.run()
```

### Hybrid Producer (`templates/hybrid_producer.py`)
Publish data to both MQTT (for real-time) and InfluxDB (for storage) simultaneously.

**Configuration example:**
```json
{
  "mqtt": {
    "broker": "localhost",
    "port": 1883
  },
  "influxdb": {
    "url": "http://localhost:8086",
    "token": "your-token",
    "org": "your-org",
    "bucket": "your-bucket"
  },
  "mqtt_topic": "sensors/data",
  "measurement": "sensors",
  "sensor_id": "sensor_001",
  "location": "lab",
  "interval": 5
}
```

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

1. Choose a template that fits your needs
2. Create a configuration file (e.g., `config.json`)
3. Customize the template for your use case
4. Run the producer:

```bash
python templates/mqtt_producer.py
```

## Creating Custom Producers

To create a custom producer, inherit from the base classes in `common/`:

```python
from common import MQTTProducer, InfluxProducer, generate_sensor_data

class MyCustomProducer:
    def __init__(self):
        self.mqtt = MQTTProducer(broker='localhost')
        self.influx = InfluxProducer(url='http://localhost:8086', ...)
        
    def generate_and_publish(self):
        data = {
            'temperature': generate_sensor_data('temperature', 22.0, 3.0),
            'humidity': generate_sensor_data('humidity', 60.0, 10.0)
        }
        
        # Publish to MQTT
        self.mqtt.publish_dict('sensors/data', data)
        
        # Write to InfluxDB
        self.influx.write_point('sensors', data)
```

## Data Generation

The `common/utils.py` module includes utilities for generating simulated sensor data:

```python
from common import generate_sensor_data, generate_batch_data, DataGenerator

# Generate single value
temp = generate_sensor_data('temperature', base_value=22.0, variance=3.0)

# Generate batch of data points
batch = generate_batch_data(
    count=100,
    measurement='sensors',
    fields={
        'temperature': ('temperature', 22.0, 3.0),
        'humidity': ('humidity', 60.0, 10.0)
    },
    tags={'location': 'lab'},
    interval_seconds=1
)

# Continuous data generator
generator = DataGenerator(
    measurement='sensors',
    fields={
        'temperature': ('temperature', 22.0, 3.0),
        'humidity': ('humidity', 60.0, 10.0)
    },
    tags={'location': 'lab'},
    interval_seconds=1
)
generator.start(callback=lambda point: print(point))
```

## Environment Variables

The utilities support environment variables for sensitive configuration:

```python
from common import get_env_variable

broker = get_env_variable('MQTT_BROKER', default='localhost')
token = get_env_variable('INFLUX_TOKEN', required=True)
```

## Examples

### Publish to MQTT
```python
with MQTTProducer(broker='localhost') as producer:
    producer.publish_dict('sensors/temp', {
        'sensor_id': 'temp_01',
        'value': 22.5,
        'unit': 'celsius'
    })
```

### Write to InfluxDB
```python
with InfluxProducer(url='http://localhost:8086', ...) as producer:
    producer.write_point(
        measurement='sensors',
        fields={'temperature': 22.5, 'humidity': 65.0},
        tags={'sensor_id': 'sensor_01', 'location': 'lab'}
    )
```

### Batch Writing
```python
producer = InfluxProducer(url='http://localhost:8086', ...)

points = [
    {
        'measurement': 'sensors',
        'fields': {'temperature': 22.5},
        'tags': {'sensor_id': 'sensor_01'}
    },
    {
        'measurement': 'sensors',
        'fields': {'temperature': 23.1},
        'tags': {'sensor_id': 'sensor_02'}
    }
]

producer.write_points(points)
producer.close()
```

## Best Practices

1. **Use Context Managers**: Both MQTT and InfluxDB producers support context managers for automatic cleanup
2. **Handle Exceptions**: Wrap publishing/writing code in try-except blocks
3. **Use Batching**: For high-frequency data, use batch operations to improve performance
4. **Monitor Connection**: Check connection status before publishing
5. **Rate Limiting**: Use the RateLimiter utility to avoid overwhelming the system

## License

MIT License
