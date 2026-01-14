# FastAPI + Dapr Agent - Reference Documentation

## Architecture Overview

Generates FastAPI microservices with Dapr sidecar integration for state management, pub/sub, and service invocation.
```
┌─────────────────────────────────────────────┐
│  FastAPI Service Pod                        │
│  ┌──────────────────┐  ┌─────────────────┐ │
│  │  FastAPI App     │  │  Dapr Sidecar   │ │
│  │  Port: 5000      │◄─┤  Port: 3500     │ │
│  │  + OpenAI Agent  │  │  + State Store  │ │
│  │  + Health Check  │  │  + Pub/Sub      │ │
│  └──────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────┘
```

## Agent Types Supported

### 1. Triage Agent
Routes user queries to specialized agents based on intent classification.

**Input Topics:** `learning.requests`
**Output Topics:** 
- `concept.requests` (explanations)
- `debug.requests` (error help)
- `exercise.requests` (coding challenges)

### 2. Concepts Agent
Explains programming concepts with examples adapted to student level.

**Input Topics:** `concept.requests`
**Output Topics:** `concept.responses`

**Capabilities:**
- Explain Python concepts (loops, functions, OOP)
- Provide code examples
- Visual diagrams (ASCII art)
- Progressive complexity

### 3. Debug Agent
Analyzes error messages and helps students fix code issues.

**Input Topics:** `debug.requests`
**Output Topics:** `debug.responses`

**Capabilities:**
- Parse Python tracebacks
- Identify root causes
- Provide hints (not full solutions)
- Suggest debugging strategies

### 4. Exercise Agent
Generates coding exercises and auto-grades submissions.

**Input Topics:** `exercise.requests`, `exercise.submissions`
**Output Topics:** `exercise.responses`, `exercise.grades`

**Capabilities:**
- Generate exercises by difficulty
- Auto-grade with test cases
- Provide partial credit
- Hint system (3 levels)

### 5. Progress Agent
Tracks student mastery and provides analytics.

**Input Topics:** `progress.requests`
**Output Topics:** `progress.updates`

**State Management:**
- User progress scores
- Streak counters
- Topic mastery levels
- Struggle patterns

## Script Parameters

### generate_agent.py
```bash
python scripts/generate_agent.py \
  --name triage \
  --type router \
  --output-dir ./services/triage
```

**Parameters:**
- `--name`: Agent name (required)
- `--type`: Agent type (router|explainer|debugger|generator|tracker)
- `--output-dir`: Output directory path
- `--port`: FastAPI port (default: 5000)
- `--dapr-port`: Dapr sidecar port (default: 3500)
- `--openai-model`: OpenAI model (default: gpt-4)

**Generated Files:**
```
services/{agent_name}/
├── app.py                    # FastAPI application
├── agent.py                  # OpenAI agent logic
├── config.py                 # Configuration
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container image
├── deployment.yaml           # K8s deployment + Dapr
├── service.yaml              # K8s service
├── dapr-component.yaml       # Dapr components
└── tests/
    └── test_agent.py         # Unit tests
```

## Dapr Components

### State Store (PostgreSQL)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  metadata:
  - name: connectionString
    value: "postgresql://user:pass@postgres:5432/db"
```

### Pub/Sub (Kafka)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.kafka
  metadata:
  - name: brokers
    value: "kafka.kafka.svc.cluster.local:9092"
  - name: consumerGroup
    value: "learnflow-agents"
```

## API Endpoints

### Health Check
```http
GET /health
Response: {"status": "healthy", "dapr": "connected"}
```

### Process Request (POST)
```http
POST /process
Content-Type: application/json

{
  "user_id": "12345",
  "query": "How do for loops work?",
  "context": {"module": "control-flow", "level": "beginner"}
}

Response:
{
  "agent": "concepts",
  "response": "For loops in Python...",
  "next_steps": ["Try exercise", "Review examples"]
}
```

### Pub/Sub Subscription (Dapr)
```http
POST /dapr-subscriber
Content-Type: application/json

{
  "topic": "learning.requests",
  "data": {
    "user_id": "12345",
    "query": "Explain list comprehensions"
  }
}
```

## Advanced Usage

### Custom Agent Prompt
```python
# Modify agent.py after generation
SYSTEM_PROMPT = """
You are a Python tutor specializing in {specialty}.
Always provide examples and encourage experimentation.
Adapt explanations to {level} level students.
"""
```

### Add New Tool
```python
# In agent.py
from openai import OpenAI

client = OpenAI()

def run_code_safely(code: str) -> dict:
    """Execute Python code in sandbox."""
    # Your sandbox implementation
    return {"output": result, "error": None}

tools = [
    {
        "type": "function",
        "function": {
            "name": "run_code_safely",
            "description": "Execute Python code securely",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"}
                }
            }
        }
    }
]
```

### State Management Example
```python
from dapr.clients import DaprClient

# Save state
with DaprClient() as client:
    client.save_state(
        store_name="statestore",
        key=f"progress:{user_id}",
        value={"mastery": 75, "streak": 5}
    )

# Load state
with DaprClient() as client:
    state = client.get_state(
        store_name="statestore",
        key=f"progress:{user_id}"
    )
    progress = state.json()
```

### Publish Event
```python
from dapr.clients import DaprClient

with DaprClient() as client:
    client.publish_event(
        pubsub_name="pubsub",
        topic_name="struggle.alerts",
        data={
            "user_id": "12345",
            "topic": "list-comprehensions",
            "error_count": 3
        }
    )
```

## Resource Requirements

### Per Agent
- CPU: 200m (request), 500m (limit)
- Memory: 256Mi (request), 512Mi (limit)
- Dapr CPU: 100m
- Dapr Memory: 128Mi

### Horizontal Scaling
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: triage-agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: triage-agent
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Troubleshooting

### Dapr Sidecar Not Ready
**Symptom:** `connection refused` on port 3500

**Diagnosis:**
```bash
kubectl logs {pod-name} -c daprd
kubectl describe pod {pod-name}
```

**Solution:**
```bash
# Ensure Dapr is initialized
dapr init -k

# Check Dapr system pods
kubectl get pods -n dapr-system

# Verify Dapr components
kubectl get components
```

### Agent Not Responding
**Symptom:** Requests timeout or return 500 errors

**Diagnosis:**
```bash
kubectl logs {pod-name} -c fastapi
kubectl port-forward {pod-name} 5000:5000
curl http://localhost:5000/health
```

**Solution:**
```bash
# Check OpenAI API key
kubectl get secret openai-credentials -o yaml

# Verify environment variables
kubectl exec {pod-name} -c fastapi -- env | grep OPENAI

# Check Dapr connectivity
kubectl exec {pod-name} -c fastapi -- curl http://localhost:3500/v1.0/healthz
```

### Message Delivery Failures
**Symptom:** Published events not received by subscribers

**Diagnosis:**
```bash
# Check Kafka topics
kubectl exec -it kafka-0 -n kafka -- kafka-topics.sh --list --bootstrap-server localhost:9092

# Check consumer groups
kubectl exec -it kafka-0 -n kafka -- kafka-consumer-groups.sh --list --bootstrap-server localhost:9092

# View Dapr logs
kubectl logs {pod-name} -c daprd
```

## Testing

### Unit Tests
```python
# tests/test_agent.py
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_process_request():
    response = client.post("/process", json={
        "user_id": "test123",
        "query": "Explain variables"
    })
    assert response.status_code == 200
    assert "response" in response.json()
```

### Integration Tests
```bash
# Deploy test agent
kubectl apply -f services/triage/deployment.yaml

# Send test message via Dapr
dapr publish --publish-app-id triage-agent \
  --pubsub pubsub \
  --topic learning.requests \
  --data '{"user_id":"test","query":"test"}'

# Verify response
kubectl logs -l app=triage-agent -c fastapi --tail=50
```

## Monitoring

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('agent_requests_total', 'Total requests')
REQUEST_DURATION = Histogram('agent_request_duration_seconds', 'Request duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Logging Best Practices
```python
import logging
import structlog

logger = structlog.get_logger()

@app.post("/process")
async def process(request: Request):
    logger.info("processing_request", 
                user_id=request.user_id,
                query_length=len(request.query))
    # ... processing ...
    logger.info("request_completed",
                user_id=request.user_id,
                duration_ms=duration)
```

## Performance Optimization

### Async OpenAI Calls
```python
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def get_completion(prompt: str):
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    async for chunk in response:
        yield chunk
```

### Connection Pooling
```python
from dapr.clients.grpc.client import DaprGrpcClient

# Reuse client connection
dapr_client = DaprGrpcClient()

async def save_state_pooled(key, value):
    await dapr_client.save_state(
        store_name="statestore",
        key=key,
        value=value
    )
```

## Security Considerations

### API Key Management
```bash
# Create secret
kubectl create secret generic openai-credentials \
  --from-literal=api-key=${OPENAI_API_KEY} \
  -n learnflow

# Reference in deployment
env:
- name: OPENAI_API_KEY
  valueFrom:
    secretKeyRef:
      name: openai-credentials
      key: api-key
```

### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: agent-netpol
spec:
  podSelector:
    matchLabels:
      app: triage-agent
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 5000
```

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Dapr Python SDK](https://docs.dapr.io/developing-applications/sdks/python/)
- [OpenAI Agents SDK](https://github.com/openai/openai-python)
- [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
