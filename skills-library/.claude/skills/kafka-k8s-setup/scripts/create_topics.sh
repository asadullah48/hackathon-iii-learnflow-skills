#!/bin/bash
set -e

echo "📝 Creating Kafka topics..."

TOPICS=(
    "learning.concept.request:3"
    "learning.concept.response:3"
    "code.execution.request:2"
    "code.execution.result:2"
    "user.progress.update:1"
    "struggle.detected:1"
    "exercise.generated:2"
)

for topic_config in "${TOPICS[@]}"; do
    IFS=':' read -r topic partitions <<< "$topic_config"
    echo "Creating: $topic ($partitions partitions)"
    kubectl exec -n kafka kafka-0 -- kafka-topics.sh \
        --create --topic "$topic" \
        --partitions "$partitions" \
        --replication-factor 1 \
        --if-not-exists \
        --bootstrap-server localhost:9092 || true
done

echo "✓ Topics created"
kubectl exec -n kafka kafka-0 -- kafka-topics.sh --list --bootstrap-server localhost:9092
