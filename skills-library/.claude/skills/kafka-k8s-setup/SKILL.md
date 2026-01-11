---
name: kafka-k8s-setup
description: Deploy Kafka on Kubernetes with topic creation and health checks
---

# Kafka K8s Setup

## When to Use
- Deploy Kafka to Kubernetes cluster
- Create topics for event-driven architecture
- Verify Kafka health and get connection strings

## Instructions

1. **Deploy**: `bash scripts/deploy.sh [dev|prod]`
2. **Create Topics**: `bash scripts/create_topics.sh`
3. **Verify**: `python scripts/verify.py`
4. **Get Connection**: `python scripts/get_connection.py`

## Outputs
- Kafka deployed with 1-3 replicas
- Topics created with proper partitions
- Connection strings for services
