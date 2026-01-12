# fastapi-dapr-agent

Generate FastAPI microservices with Dapr integration for LearnFlow AI agents.

## Usage
```bash
# Generate Triage agent
python scripts/generate_agent.py triage

# Generate Concepts agent
python scripts/generate_agent.py concepts

# Generate Debug agent
python scripts/generate_agent.py debug

# Generate Exercise agent
python scripts/generate_agent.py exercise

# Generate Progress agent
python scripts/generate_agent.py progress

# Build Docker image
cd {agent_name} && docker build -t {agent_name}-agent .

# Deploy to Kubernetes
kubectl apply -f {agent_name}/k8s/
```

## Features

- **Async FastAPI**: Non-blocking I/O for high throughput
- **Dapr Pub/Sub**: Kafka integration via Dapr sidecar
- **Dapr State**: PostgreSQL state management
- **LLM Integration**: OpenAI/Gemini templates
- **K8s Ready**: Deployment manifests with Dapr annotations
- **Health Endpoints**: `/health`, `/ready` for liveness/readiness

## Agents

1. **Triage**: Routes queries to specialized agents
2. **Concepts**: Explains programming concepts
3. **Debug**: Analyzes errors and suggests fixes
4. **Exercise**: Generates coding exercises
5. **Progress**: Tracks learning progress

## Configuration

Set via environment variables:
- `DAPR_HTTP_PORT`: 3500 (default)
- `PUBSUB_NAME`: kafka-pubsub
- `STATE_STORE`: postgres-state
- `LLM_API_KEY`: Your API key
- `LLM_MODEL`: gpt-4 (or gemini-pro)

## Token Usage

- SKILL.md: ~195 tokens
- Generated code: External files (0 tokens)
- Results: ~45 tokens (paths + status)
