# fastapi-dapr-agent Skill Specification

**Version:** 1.0.0  
**Status:** Draft  
**Owner:** Asadullah (asadullah48)  
**Created:** 2026-01-12  
**Hackathon:** Panaversity Hackathon III - LearnFlow

---

## 1. Overview

### 1.1 Purpose
Generate production-ready FastAPI microservices with Dapr sidecar integration for event-driven AI agent architecture. Supports LearnFlow's 5 specialized agents with Kafka pub/sub, PostgreSQL state management, and Kubernetes deployment.

### 1.2 Scope
**In Scope:**
- FastAPI service scaffolding with async/await
- Dapr sidecar integration (pub/sub, state, invoke)
- Agent-specific code generation (Triage, Concepts, Debug, Exercise, Progress)
- Kafka event handlers via Dapr
- PostgreSQL state management via Dapr
- Health/readiness endpoints
- Dockerfile with Dapr-compatible base
- Kubernetes manifests with Dapr annotations
- OpenAI/LLM integration templates

**Out of Scope:**
- Frontend code (handled by nextjs-k8s-deploy)
- Database schema (handled by postgres-k8s-setup)
- Kafka setup (handled by kafka-k8s-setup)

### 1.3 Token Budget
- **SKILL.md:** ≤200 tokens (comprehensive but efficient)
- **Generated templates:** 0 tokens (external files)
- **Agent results:** ≤50 tokens (status + file paths)
- **Total:** ≤250 tokens per invocation

### 1.4 Success Metrics
- **Autonomy:** 85% (some agent logic requires user input)
- **Efficiency:** 93% (template-based generation)
- **Cross-agent compatibility:** 98% (standard FastAPI/Dapr patterns)

---

## 2. User Stories

### US1: Generate Triage Agent
**As a** hackathon participant  
**I want** to generate the Triage agent microservice  
**So that** it routes user queries to specialized agents via Kafka

**Acceptance Criteria:**
- FastAPI service with `/triage` endpoint
- Dapr pub/sub publishes to `triage-requests` topic
- LLM determines target agent (concepts/debug/exercise)
- State stored in Dapr (user context)
- Kubernetes manifest with Dapr annotations

### US2: Generate Concepts Agent
**As a** hackathon participant  
**I want** to generate the Concepts agent  
**So that** it explains programming concepts with examples

**Acceptance Criteria:**
- Subscribes to `concept-requests` via Dapr
- LLM generates explanations with code examples
- Publishes results to `concept-responses`
- Stores concept definitions in Dapr state

### US3: Generate Debug Agent
**As a** hackathon participant  
**I want** to generate the Debug agent  
**So that** it analyzes code errors and suggests fixes

**Acceptance Criteria:**
- Subscribes to `debug-requests` via Dapr
- LLM analyzes stack traces and code
- Publishes fixes to `debug-responses`
- Stores debug sessions in Dapr state

### US4: Generate Exercise Agent
**As a** hackathon participant  
**I want** to generate the Exercise agent  
**So that** it creates coding exercises and evaluates solutions

**Acceptance Criteria:**
- Subscribes to `exercise-requests` via Dapr
- LLM generates exercises with test cases
- Executes code via MCP (handled externally)
- Publishes results to `exercise-responses`

### US5: Generate Progress Agent
**As a** hackathon participant  
**I want** to generate the Progress agent  
**So that** it tracks learning progress and suggests next steps

**Acceptance Criteria:**
- Subscribes to `progress-requests` via Dapr
- Queries PostgreSQL via Dapr for learning history
- LLM analyzes strengths/weaknesses
- Publishes recommendations to `progress-responses`

---

## 3. Functional Requirements

### FR1: Service Scaffolding
**Description:** Generate FastAPI service structure with async patterns

**Inputs:**
- `agent_name` (triage|concepts|debug|exercise|progress)
- `port` (default: 8000)
- `llm_provider` (openai|gemini|anthropic, default: openai)

**Outputs:**
````
{agent_name}/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app with Dapr integration
│   ├── config.py            # Environment config
│   ├── models.py            # Pydantic models
│   ├── agent.py             # Agent-specific logic
│   └── dapr_client.py       # Dapr helper functions
├── Dockerfile
├── requirements.txt
└── k8s/
    └── deployment.yaml      # With Dapr annotations
````

**Behavior:**
- All routes use `async def` for non-blocking I/O
- Dapr HTTP API port 3500 (sidecar default)
- Health endpoints: `/health`, `/ready`
- Graceful shutdown handling

### FR2: Dapr Pub/Sub Integration
**Description:** Kafka event publishing/subscribing via Dapr

**Inputs:**
- Topic names (derived from agent type)
- Pubsub component name (default: `kafka-pubsub`)

**Generated Code:**
````python
# Publishing
await dapr_client.publish_event(
    pubsub_name="kafka-pubsub",
    topic_name="triage-requests",
    data={"user_id": "...", "query": "..."}
)

# Subscribing
@app.post("/dapr/subscribe")
async def subscribe():
    return [{
        "pubsubname": "kafka-pubsub",
        "topic": "concept-requests",
        "route": "/on-concept-request"
    }]

@app.post("/on-concept-request")
async def handle_concept(event: CloudEvent):
    data = event.data
    # Process event...
````

**Behavior:**
- CloudEvent format compliance
- Automatic JSON serialization
- Error handling with dead-letter queue support

### FR3: Dapr State Management
**Description:** PostgreSQL state operations via Dapr state API

**Inputs:**
- State store name (default: `postgres-state`)
- Key naming convention (e.g., `user:{user_id}`)

**Generated Code:**
````python
# Save state
await dapr_client.save_state(
    store_name="postgres-state",
    key=f"user:{user_id}",
    value={"context": "...", "history": [...]}
)

# Get state
state = await dapr_client.get_state(
    store_name="postgres-state",
    key=f"user:{user_id}"
)

# Query state (metadata)
await dapr_client.query_state(
    store_name="postgres-state",
    query={"filter": {"EQ": {"user_id": "..."}}}
)
````

**Behavior:**
- Automatic JSON serialization
- Optimistic concurrency with ETags
- Bulk operations support

### FR4: Agent-Specific Logic
**Description:** LLM integration templates for each agent type

**Triage Agent:**
````python
async def route_query(query: str) -> str:
    """Determine target agent using LLM"""
    prompt = f"Route this query to concepts/debug/exercise: {query}"
    response = await llm_client.complete(prompt)
    return parse_agent(response)
````

**Concepts Agent:**
````python
async def explain_concept(concept: str) -> dict:
    """Generate explanation with examples"""
    prompt = f"Explain {concept} with Python examples"
    response = await llm_client.complete(prompt)
    return {
        "explanation": response.text,
        "examples": parse_code_blocks(response)
    }
````

**Debug Agent:**
````python
async def analyze_error(code: str, error: str) -> dict:
    """Analyze error and suggest fix"""
    prompt = f"Fix this error:\n{code}\n\nError: {error}"
    response = await llm_client.complete(prompt)
    return {
        "diagnosis": response.analysis,
        "fix": response.suggested_code
    }
````

**Exercise Agent:**
````python
async def generate_exercise(concept: str, difficulty: int) -> dict:
    """Create coding exercise with tests"""
    prompt = f"Create {difficulty}/10 difficulty exercise for {concept}"
    response = await llm_client.complete(prompt)
    return {
        "problem": response.description,
        "starter_code": response.template,
        "tests": parse_test_cases(response)
    }
````

**Progress Agent:**
````python
async def analyze_progress(user_id: str) -> dict:
    """Analyze learning progress from DB"""
    history = await dapr_client.query_state(...)
    prompt = f"Analyze progress: {history}"
    response = await llm_client.complete(prompt)
    return {
        "strengths": response.strengths,
        "weaknesses": response.weaknesses,
        "next_steps": response.recommendations
    }
````

### FR5: Kubernetes Deployment
**Description:** Generate K8s manifests with Dapr annotations

**Generated Manifest:**
````yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {agent_name}-agent
spec:
  replicas: 1
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "{agent_name}-agent"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
    spec:
      containers:
      - name: {agent_name}
        image: {agent_name}-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: DAPR_HTTP_PORT
          value: "3500"
        - name: PUBSUB_NAME
          value: "kafka-pubsub"
        - name: STATE_STORE
          value: "postgres-state"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: {agent_name}-agent
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8000
````

---

## 4. Technical Requirements

### 4.1 Dependencies
**Python (requirements.txt):**
````
fastapi==0.109.0
uvicorn[standard]==0.27.0
dapr==1.12.0
pydantic==2.5.3
pydantic-settings==2.1.0
openai==1.10.0
httpx==0.26.0
python-json-logger==2.0.7
````

### 4.2 Dockerfile Template
````dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY app/ ./app/

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
````

### 4.3 Configuration
**Environment Variables:**
- `DAPR_HTTP_PORT`: Dapr sidecar HTTP port (default: 3500)
- `DAPR_GRPC_PORT`: Dapr sidecar gRPC port (default: 50001)
- `PUBSUB_NAME`: Kafka pubsub component name
- `STATE_STORE`: PostgreSQL state store name
- `LLM_API_KEY`: OpenAI/Gemini API key
- `LLM_MODEL`: Model name (gpt-4, gemini-pro, etc.)
- `LOG_LEVEL`: info|debug|warning

---

## 5. LearnFlow Agent Mappings

### 5.1 Event Flow
````
User Query → Next.js Frontend
    ↓ HTTP POST
Triage Agent
    ↓ Kafka: triage-requests
[Concepts | Debug | Exercise] Agent
    ↓ Kafka: {agent}-responses
Progress Agent (analyzes outcomes)
    ↓ PostgreSQL via Dapr
Progress Dashboard
````

### 5.2 Topic Naming
- **triage-requests**: User queries for routing
- **concept-requests**: Concept explanation requests
- **concept-responses**: Concept explanations
- **debug-requests**: Code debugging requests
- **debug-responses**: Debug solutions
- **exercise-requests**: Exercise generation requests
- **exercise-responses**: Generated exercises
- **exercise-submissions**: User code submissions
- **exercise-results**: Execution results
- **progress-requests**: Progress analysis requests
- **progress-responses**: Progress reports

### 5.3 State Keys
- `user:{user_id}`: User profile and preferences
- `session:{session_id}`: Active learning session
- `concept:{concept_id}`: Concept definitions cache
- `exercise:{exercise_id}`: Exercise templates
- `progress:{user_id}`: Learning progress data

---

## 6. Testing Plan

### 6.1 Unit Tests
**Test Categories:**
1. **Dapr Integration**
   - Mock Dapr sidecar responses
   - Test pub/sub serialization
   - Test state operations

2. **Agent Logic**
   - Mock LLM responses
   - Test query routing (Triage)
   - Test explanation generation (Concepts)
   - Test error analysis (Debug)
   - Test exercise generation (Exercise)
   - Test progress analysis (Progress)

3. **Error Handling**
   - Dapr sidecar unavailable
   - Kafka connection failures
   - PostgreSQL timeouts
   - LLM API errors

**Coverage Target:** 80%

### 6.2 Integration Tests
**Scenarios:**
1. **End-to-End Flow**
   - Send query to Triage
   - Verify Kafka event published
   - Verify Concepts agent receives event
   - Verify response published
   - Verify state saved

2. **Multi-Agent Coordination**
   - Exercise request → generation → submission → evaluation
   - Progress tracking across multiple interactions

3. **Kubernetes Deployment**
   - Deploy to Minikube
   - Verify Dapr sidecar injection
   - Test service-to-service invocation
   - Test health endpoints

### 6.3 Performance Tests
**Metrics:**
- Request latency: <500ms (p95)
- Event processing: <1s (end-to-end)
- State operations: <100ms
- Memory usage: <256Mi (steady state)
- CPU usage: <100m (steady state)

---

## 7. SKILL.md Content
````markdown
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
````

---

## 8. Implementation Notes

### 8.1 Code Generation Strategy
1. **Template-based**: Use Jinja2 templates for all files
2. **Agent-specific injection**: Custom logic per agent type
3. **Minimal placeholders**: Pre-fill sensible defaults
4. **Comment annotations**: Link code to spec sections (e.g., `# Implements FR2`)

### 8.2 Security Considerations
- **API keys**: Never hardcode, use environment variables
- **Input validation**: Pydantic models for all requests
- **Rate limiting**: Implement per-user limits
- **Secrets**: Use Kubernetes Secrets for sensitive data

### 8.3 Observability
- **Structured logging**: JSON format with correlation IDs
- **Metrics**: Expose Prometheus endpoints
- **Tracing**: Dapr distributed tracing enabled
- **Health checks**: Liveness checks Dapr sidecar connectivity

### 8.4 Future Enhancements
- **Streaming responses**: SSE for LLM streaming
- **Circuit breakers**: Resilience4j integration
- **Canary deployments**: Gradual rollouts
- **A/B testing**: LLM model comparison

---

## 9. Acceptance Criteria

**Skill is complete when:**
- ✅ All 5 agents can be generated via single command
- ✅ Dapr pub/sub integration works with Kafka
- ✅ Dapr state integration works with PostgreSQL
- ✅ LLM integration templates functional
- ✅ Kubernetes manifests deploy successfully to Minikube
- ✅ Health endpoints return 200 OK
- ✅ Token budget ≤250 tokens
- ✅ No manual editing required for basic use cases

---

**End of Specification**
