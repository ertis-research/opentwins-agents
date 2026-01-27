# Agent Templates Workspace

A comprehensive template workspace for creating data consumer and producer agents with built-in support for MQTT and InfluxDB.

## Overview

This workspace provides ready-to-use templates and utilities for building data agents that can:
- **Consume** data from MQTT topics and InfluxDB databases
- **Produce** data to MQTT brokers and InfluxDB time-series databases
- **Process** and transform data in real-time
- **Combine** multiple data sources and destinations

## Structure

```
templates/
├── data-consumer/          # Data consumer agents
│   ├── common/            # Shared utilities
│   │   ├── mqtt_client.py
│   │   ├── influx_client.py
│   │   └── utils.py
│   ├── templates/         # Ready-to-use templates
│   │   ├── basic_consumer.py
│   │   ├── mqtt_consumer.py
│   │   ├── influx_consumer.py
│   │   └── hybrid_consumer.py
│   ├── config.example.json
│   ├── requirements.txt
│   └── README.md
│
└── data-producer/          # Data producer agents
    ├── common/            # Shared utilities
    │   ├── mqtt_client.py
    │   ├── influx_client.py
    │   └── utils.py
    ├── templates/         # Ready-to-use templates
    │   ├── basic_producer.py
    │   ├── mqtt_producer.py
    │   ├── influx_producer.py
    │   ├── hybrid_producer.py
    │   └── tensorflow_producer.py
    ├── config.example.json
    ├── config.tensorflow.example.json
    ├── requirements.txt
    └── README.md
```


### Install dependencies

For data consumer:
```bash
cd data-consumer
pip install -r requirements.txt
```

For data producer:
```bash
cd data-producer
pip install -r requirements.txt
```

### Configure the agent

Copy the example configuration and customize it:

```bash
# For consumer
cd data-consumer
cp config.example.json config.json
# Edit config.json with your settings

# For producer
cd data-producer
cp config.example.json config.json
# Edit config.json with your settings
```

### Run a Template

**MQTT Producer Example:**
```bash
cd data-producer
python templates/mqtt_producer.py
```

**MQTT Consumer Example:**
```bash
cd data-consumer
python templates/mqtt_consumer.py
```

**InfluxDB Producer Example:**
```bash
cd data-producer
python templates/influx_producer.py
```

**InfluxDB Consumer Example:**
```bash
cd data-consumer
python templates/influx_consumer.py
```

**TensorFlow Producer Example:**
```bash
cd data-producer
cp config.tensorflow.example.json config.json
# Edit config.json with your model path
python templates/tensorflow_producer.py
```


### Available Templates

### Data Consumer Templates
1. **basic_consumer.py** - Simple consumer template for custom implementations
2. **mqtt_consumer.py** - Subscribe to MQTT topics and process messages
3. **influx_consumer.py** - Query and analyze InfluxDB time-series data
4. **hybrid_consumer.py** - Combine MQTT real-time data with InfluxDB historical queries

### Data Producer Templates
1. **basic_producer.py** - Simple producer template for custom implementations
2. **mqtt_producer.py** - Publish sensor data to MQTT topics
3. **influx_producer.py** - Write time-series data to InfluxDB
4. **hybrid_producer.py** - Simultaneously publish to MQTT and write to InfluxDB
5. **tensorflow_producer.py** - Load ML models and publish predictions

## Machine Learning Integration

The TensorFlow producer template supports:
- **Classification Models**: Output class labels with confidence scores
- **Regression Models**: Single or multi-output predictions
- **Preprocessing**: Normalization, scaling, custom transformations
- **Batch Processing**: Process multiple inputs efficiently
- **Continuous Mode**: Real-time predictions at configurable intervals


## Docker

Each agent must be containerized. Example Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "templates/mqtt_producer.py"]
```