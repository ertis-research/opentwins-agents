# Data Consumer Templates

This folder contains templates and utilities for creating data consumer agents.

## Structure

```
data-consumer/
├── common/                 # Shared utilities and clients
│   ├── __init__.py        # Module exports
│   ├── mqtt_client.py     # MQTT consumer client
│   ├── influx_client.py   # InfluxDB consumer client
│   └── utils.py           # Common helper functions
├── templates/             # Agent templates
│   ├── basic_consumer.py  # Basic consumer template
│   ├── mqtt_consumer.py   # MQTT-specific consumer
│   ├── influx_consumer.py # InfluxDB-specific consumer
│   └── hybrid_consumer.py # Combined MQTT + InfluxDB consumer
└── requirements.txt       # Python dependencies
```

## Common Utilities

### MQTT Client (`common/mqtt_client.py`)
- **MQTTConsumer**: Subscribe to MQTT topics and consume messages
- Features:
  - Automatic JSON parsing
  - Customizable callbacks
  - Support for TLS/SSL
  - Authentication support
  - Wildcard topic subscriptions

### InfluxDB Client (`common/influx_client.py`)
- **InfluxConsumer**: Query and read data from InfluxDB
- Features:
  - Time range queries
  - Aggregation support (mean, sum, min, max)
  - Last N values queries
  - Flexible Flux queries
  - Tag-based filtering

### Utilities (`common/utils.py`)
- Configuration loading/saving
- Environment variable handling
- Timestamp conversion utilities
- Retry with exponential backoff
- Data validation
- Rate limiting

## Templates

### Basic Consumer (`templates/basic_consumer.py`)
Simple template for creating custom consumer agents.

```python
from templates.basic_consumer import BasicConsumer

consumer = BasicConsumer('config.json')
consumer.run()
```

### MQTT Consumer (`templates/mqtt_consumer.py`)
Subscribe to MQTT topics and process messages in real-time.

**Configuration example:**
```json
{
  "mqtt": {
    "broker": "localhost",
    "port": 1883,
    "client_id": "my_consumer",
    "username": "user",
    "password": "pass"
  },
  "topics": ["sensors/#", "events/+"]
}
```

**Usage:**
```python
from templates.mqtt_consumer import MQTTDataConsumer

consumer = MQTTDataConsumer('config.json')
consumer.run()
```

### InfluxDB Consumer (`templates/influx_consumer.py`)
Query and analyze data from InfluxDB.

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
  "field": "temperature"
}
```

**Usage:**
```python
from templates.influx_consumer import InfluxDataConsumer

consumer = InfluxDataConsumer('config.json')
consumer.run()
```

### Hybrid Consumer (`templates/hybrid_consumer.py`)
Combine real-time MQTT data with historical InfluxDB queries.

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
  "topics": ["sensors/#"],
  "measurement": "sensors",
  "field": "temperature"
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
4. Run the consumer:

```bash
python templates/mqtt_consumer.py
```

## Creating Custom Consumers

To create a custom consumer, inherit from the base classes in `common/`:

```python
from common import MQTTConsumer, InfluxConsumer

class MyCustomConsumer:
    def __init__(self):
        self.mqtt = MQTTConsumer(broker='localhost')
        self.influx = InfluxConsumer(url='http://localhost:8086', ...)
        
    def on_message(self, topic, payload):
        # Process MQTT message
        # Query InfluxDB if needed
        pass
```

## Environment Variables

The utilities support environment variables for sensitive configuration:

```python
from common import get_env_variable

broker = get_env_variable('MQTT_BROKER', default='localhost')
token = get_env_variable('INFLUX_TOKEN', required=True)
```

## Examples

### Subscribe to multiple topics
```python
consumer = MQTTConsumer(broker='localhost')
consumer.set_message_callback(lambda topic, msg: print(f"{topic}: {msg}"))
consumer.connect()
consumer.subscribe('sensors/+/temperature')
consumer.subscribe('events/#')
consumer.start()
```

### Query time-series data
```python
from datetime import datetime, timedelta

consumer = InfluxConsumer(url='http://localhost:8086', ...)
start = datetime.now() - timedelta(hours=24)
results = consumer.query_range(
    measurement='sensors',
    field='temperature',
    start=start
)
```

## License

MIT License
