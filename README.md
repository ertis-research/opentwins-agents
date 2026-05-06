# OpenTwins Agent Framework (Alpha)

This repository contains the **agent management and deployment framework** developed as an **alpha version** extension of the OpenTwins digital twin platform. The framework enables the definition, deployment, execution, and monitoring of autonomous agents that operate as first-class components of a digital twin.

⚠️ **Alpha status**  
This software is currently in **alpha stage**. APIs, internal components, and deployment workflows may change. The framework is intended primarily for **research, experimentation, and early validation**, and it is not yet recommended for production environments.

The tool is designed to support **agent-based digital twins** for complex and dynamic environments, with a particular focus on **energy management**, flexibility services, and simulation-driven decision support.

---

## Architecture Overview

The framework follows a microservices-based architecture fully aligned with the OpenTwins platform. Each agent is deployed as an independent Docker container and managed through a dedicated Agent Management Service.

Core components include:

- **Agent Management Service**
  - Deployment, start/stop, and removal of agents  
  - Monitoring of agent status and execution logs  
  - REST API for external integration  

- **Agent Templates**
  - Standardized project structures  
  - Preconfigured communication and data access layers  
  - Utilities for scheduling, simulation, and prediction services  

- **Persistence and Storage**
  - PostgreSQL for configuration and metadata  
  - MinIO for models, FMUs, and execution artifacts  

Agents interact with shared Digital Twin models, enabling coordinated operation across simulation, prediction, and control tasks.

---

## Supported Agent Types

The framework supports heterogeneous agents, including:

- **Monitoring Agents** – Data acquisition and preprocessing  
- **Simulation Agents** – FMI-based simulations and what-if analysis  
- **Prediction Agents** – Forecasting and ML-based inference  
- **Control Agents** – Flexibility and operational control  
- **Coordination Agents** – Constraint handling and multi-agent orchestration  
- **Visualization Agents** – Dashboards and decision-support interfaces  

---

## Deployment Workflow

Agent deployment follows a structured workflow defined in the architecture:

1. Agent design and objective definition  
2. Selection of an appropriate agent template  
3. Implementation of domain-specific logic  
4. Docker image build and packaging  
5. Publication to a container registry  
6. Deployment via the Agent Management Service  
7. Monitoring and visualization through OpenTwins tools  

This workflow ensures reproducibility, modularity, and ease of adoption.

---
## API Endpoints

| Method | Path | Parameters | Response |
|--------|------|------------|----------|
| `GET` | `/agents/` | Query: `context` (opt.), `twin` (opt.) | `200` agent list · `404` empty list |
| `GET` | `/agents/{pod}/logs` | Path: `pod` | `200` pod logs · `404` empty list |
| `POST` | `/agent/{context}/{agentId}` | Path: `context`, `agentId` · Body: JSON with agent definition | `200` deployed · `422` already exists · `500` error |
| `DELETE` | `/agent/{context}/{agentId}` | Path: `context`, `agentId` | `200` deleted · error message |
| `POST` | `/agent/{context}/{agentId}/pause` | Path: `context`, `agentId` | `200` paused · `404` error |
| `POST` | `/agent/{context}/{agentId}/resume` | Path: `context`, `agentId` | `200` resumed · `404` error |
| `GET` | `/agent/{context}/{agentId}` | Path: `context`, `agentId` | `200` agent info · error message |
| `GET` | `/agent/{context}/{agentId}/logs` | Path: `context`, `agentId` | `200` agent logs · error message |
| `PUT` | `/agent/{context}/{agentId}/twin/{twinId}/link` | Path: `context`, `agentId`, `twinId` | `200` linked · `404` error |
| `PUT` | `/agent/{context}/{agentId}/twin/{twinId}/unlink` | Path: `context`, `agentId`, `twinId` | `200` unlinked · `404` error |
---

## Installation

### Prerequisites

- Docker
- Kubernetes
- Running OpenTwins instance  
- PostgreSQL  
- MinIO or compatible object storage

Just apply all kubernetes YAMLS with your configuration
