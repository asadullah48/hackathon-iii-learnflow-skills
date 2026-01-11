#!/bin/bash
set -e

ENV=${1:-dev}

echo "🚀 Deploying Kafka ($ENV environment)..."

if [ "$ENV" = "prod" ]; then
    REPLICAS=3
    MEMORY="2Gi"
    CPU="1"
else
    REPLICAS=1
    MEMORY="512Mi"
    CPU="500m"
fi

kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -

cat <<EOFMANIFEST | kubectl apply -f -
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: kafka
  namespace: kafka
spec:
  serviceName: kafka
  replicas: $REPLICAS
  selector:
    matchLabels:
      app: kafka
  template:
    metadata:
      labels:
        app: kafka
    spec:
      containers:
      - name: kafka
        image: bitnami/kafka:latest
        ports:
        - containerPort: 9092
        resources:
          requests:
            memory: "$MEMORY"
            cpu: "$CPU"
        env:
        - name: KAFKA_CFG_ZOOKEEPER_CONNECT
          value: "zookeeper:2181"
---
apiVersion: v1
kind: Service
metadata:
  name: kafka
  namespace: kafka
spec:
  ports:
  - port: 9092
  selector:
    app: kafka
EOFMANIFEST

echo "✓ Kafka deployed"
kubectl get pods -n kafka
