#!/usr/bin/env python3
"""
FastAPI + Dapr Agent Generator
Implements FR1-FR5 from fastapi-dapr-agent_SPEC.md
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

# Agent configurations (implements section 5: LearnFlow Agent Mappings)
AGENT_CONFIGS = {
    "triage": {
        "description": "Routes user queries to specialized agents",
        "subscribe_topics": [],
        "publish_topics": ["triage-requests"],
        "llm_prompt_template": "Route this query to concepts/debug/exercise: {query}"
    },
    "concepts": {
        "description": "Explains programming concepts with examples",
        "subscribe_topics": ["concept-requests"],
        "publish_topics": ["concept-responses"],
        "llm_prompt_template": "Explain {concept} with Python examples"
    },
    "debug": {
        "description": "Analyzes code errors and suggests fixes",
        "subscribe_topics": ["debug-requests"],
        "publish_topics": ["debug-responses"],
        "llm_prompt_template": "Fix this error:\n{code}\n\nError: {error}"
    },
    "exercise": {
        "description": "Generates coding exercises and evaluates solutions",
        "subscribe_topics": ["exercise-requests", "exercise-submissions"],
        "publish_topics": ["exercise-responses", "exercise-results"],
        "llm_prompt_template": "Create {difficulty}/10 difficulty exercise for {concept}"
    },
    "progress": {
        "description": "Tracks learning progress and suggests next steps",
        "subscribe_topics": ["progress-requests"],
        "publish_topics": ["progress-responses"],
        "llm_prompt_template": "Analyze progress: {history}"
    }
}


def generate_main_py(agent_name: str, config: Dict[str, Any]) -> str:
    """Generate main.py with FastAPI app and Dapr integration (FR1, FR2)"""
    
    subscribe_routes = "\n".join([
        f'''    {{
        "pubsubname": "kafka-pubsub",
        "topic": "{topic}",
        "route": "/on-{topic.replace('-', '_')}"
    }},'''
        for topic in config["subscribe_topics"]
    ])
    
    event_handlers = "\n\n".join([
        f'''@app.post("/on-{topic.replace('-', '_')}")
async def handle_{topic.replace('-', '_')}(event: dict):
    """Handle {topic} events (implements FR2: Dapr Pub/Sub)"""
    data = event.get("data", {{}})
    logger.info(f"Received {topic} event", extra={{"data": data}})
    
    try:
        # Process with agent logic (implements FR4)
        result = await agent.process(data)
        
        # Publish response (implements FR2)
        await publish_event("{config['publish_topics'][0] if config['publish_topics'] else 'responses'}", result)
        
        return {{"status": "success"}}
    except Exception as e:
        logger.error(f"Error processing {topic}", exc_info=True)
        return {{"status": "error", "message": str(e)}}'''
        for topic in config["subscribe_topics"]
    ])
    
    return f'''"""
{agent_name.capitalize()} Agent - {config['description']}
Implements FR1, FR2, FR3, FR4 from fastapi-dapr-agent_SPEC.md
"""

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import logging
from app.config import settings
from app.agent import {agent_name.capitalize()}Agent
from app.dapr_client import publish_event, save_state, get_state

# Configure logging (section 8.3: Observability)
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info(f"Starting {{settings.AGENT_NAME}} agent")
    yield
    logger.info(f"Shutting down {{settings.AGENT_NAME}} agent")


app = FastAPI(
    title="{agent_name.capitalize()} Agent",
    description="{config['description']}",
    version="1.0.0",
    lifespan=lifespan
)

# Initialize agent (implements FR4: Agent-Specific Logic)
agent = {agent_name.capitalize()}Agent()


# Health endpoints (implements FR1: Service Scaffolding)
@app.get("/health")
async def health():
    """Liveness probe"""
    return {{"status": "healthy", "agent": "{agent_name}"}}


@app.get("/ready")
async def ready():
    """Readiness probe - checks Dapr sidecar"""
    try:
        # Test Dapr connectivity
        await get_state("postgres-state", "health-check")
        return {{"status": "ready", "dapr": "connected"}}
    except Exception as e:
        logger.error("Dapr not ready", exc_info=True)
        raise HTTPException(status_code=503, detail="Dapr unavailable")


# Dapr subscription endpoint (implements FR2: Dapr Pub/Sub)
@app.get("/dapr/subscribe")
async def subscribe():
    """Register topic subscriptions"""
    return [
{subscribe_routes}
    ]


# Event handlers (implements FR2 + FR4)
{event_handlers}


# Main endpoint for direct invocation (implements FR1)
@app.post("/{agent_name}")
async def process_request(request: dict):
    """Main processing endpoint"""
    try:
        result = await agent.process(request)
        return {{"status": "success", "result": result}}
    except Exception as e:
        logger.error(f"Error in {{settings.AGENT_NAME}}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
'''


def generate_agent_py(agent_name: str, config: Dict[str, Any]) -> str:
    """Generate agent.py with LLM integration (FR4: Agent-Specific Logic)"""
    
    return f'''"""
{agent_name.capitalize()} Agent Logic
Implements FR4: Agent-Specific Logic from fastapi-dapr-agent_SPEC.md
"""

import logging
from typing import Dict, Any
from openai import AsyncOpenAI
from app.config import settings
from app.dapr_client import save_state, get_state, query_state

logger = logging.getLogger(__name__)


class {agent_name.capitalize()}Agent:
    """
    {config['description']}
    
    LLM Prompt Template: {config['llm_prompt_template']}
    """
    
    def __init__(self):
        self.llm_client = AsyncOpenAI(api_key=settings.LLM_API_KEY)
        self.model = settings.LLM_MODEL
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing logic (implements FR4)"""
        logger.info(f"Processing {{data}}")
        
        # Get user context from state (implements FR3: Dapr State)
        user_id = data.get("user_id", "anonymous")
        context = await self._get_context(user_id)
        
        # Process with LLM (implements FR4)
        result = await self._llm_process(data, context)
        
        # Save updated context (implements FR3)
        await self._save_context(user_id, result)
        
        return result
    
    async def _get_context(self, user_id: str) -> Dict[str, Any]:
        """Retrieve user context from Dapr state (implements FR3)"""
        state = await get_state("postgres-state", f"user:{{user_id}}")
        return state or {{"history": [], "preferences": {{}}}}
    
    async def _save_context(self, user_id: str, result: Dict[str, Any]):
        """Save updated context to Dapr state (implements FR3)"""
        context = await self._get_context(user_id)
        context["history"].append(result)
        await save_state("postgres-state", f"user:{{user_id}}", context)
    
    async def _llm_process(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Process with LLM (agent-specific implementation)"""
        # Build prompt from template
        prompt = self._build_prompt(data, context)
        
        try:
            response = await self.llm_client.chat.completions.create(
                model=self.model,
                messages=[
                    {{"role": "system", "content": "You are a {config['description']} assistant."}},
                    {{"role": "user", "content": prompt}}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            return self._parse_response(content, data)
            
        except Exception as e:
            logger.error(f"LLM error: {{e}}", exc_info=True)
            return {{"error": str(e), "status": "failed"}}
    
    def _build_prompt(self, data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build LLM prompt from template and data"""
        # Agent-specific prompt building
        template = "{config['llm_prompt_template']}"
        return template.format(**data)
    
    def _parse_response(self, content: str, original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        return {{
            "agent": "{agent_name}",
            "response": content,
            "metadata": original_data
        }}
'''


def generate_config_py() -> str:
    """Generate config.py with environment variables (section 4.3: Configuration)"""
    
    return '''"""
Configuration from environment variables
Implements section 4.3: Configuration from fastapi-dapr-agent_SPEC.md
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Agent config
    AGENT_NAME: str = "agent"
    PORT: int = 8000
    
    # Dapr config (section 4.3)
    DAPR_HTTP_PORT: int = 3500
    DAPR_GRPC_PORT: int = 50001
    PUBSUB_NAME: str = "kafka-pubsub"
    STATE_STORE: str = "postgres-state"
    
    # LLM config (section 4.3)
    LLM_API_KEY: str
    LLM_MODEL: str = "gpt-4"
    LLM_PROVIDER: str = "openai"
    
    # Observability (section 8.3)
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
'''


def generate_dapr_client_py() -> str:
    """Generate dapr_client.py with helper functions (FR2, FR3)"""
    
    return '''"""
Dapr Client Helper Functions
Implements FR2 (Pub/Sub) and FR3 (State) from fastapi-dapr-agent_SPEC.md
"""

import httpx
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

# Dapr sidecar base URL
DAPR_BASE = f"http://localhost:{settings.DAPR_HTTP_PORT}/v1.0"


async def publish_event(topic: str, data: Dict[str, Any]) -> bool:
    """
    Publish event to Kafka via Dapr (implements FR2: Dapr Pub/Sub)
    
    Args:
        topic: Kafka topic name
        data: Event data (will be JSON-serialized)
    
    Returns:
        True if published successfully
    """
    url = f"{DAPR_BASE}/publish/{settings.PUBSUB_NAME}/{topic}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            logger.info(f"Published to {topic}")
            return True
    except Exception as e:
        logger.error(f"Failed to publish to {topic}: {e}", exc_info=True)
        return False


async def save_state(store: str, key: str, value: Dict[str, Any]) -> bool:
    """
    Save state to PostgreSQL via Dapr (implements FR3: Dapr State)
    
    Args:
        store: State store name (e.g., "postgres-state")
        key: State key (e.g., "user:123")
        value: State value (will be JSON-serialized)
    
    Returns:
        True if saved successfully
    """
    url = f"{DAPR_BASE}/state/{store}"
    
    payload = [{
        "key": key,
        "value": value
    }]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            logger.debug(f"Saved state: {key}")
            return True
    except Exception as e:
        logger.error(f"Failed to save state {key}: {e}", exc_info=True)
        return False


async def get_state(store: str, key: str) -> Optional[Dict[str, Any]]:
    """
    Get state from PostgreSQL via Dapr (implements FR3: Dapr State)
    
    Args:
        store: State store name
        key: State key
    
    Returns:
        State value or None if not found
    """
    url = f"{DAPR_BASE}/state/{store}/{key}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            
            if response.status_code == 204:
                return None
            
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        logger.error(f"Failed to get state {key}: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Failed to get state {key}: {e}", exc_info=True)
        return None


async def query_state(store: str, query: Dict[str, Any]) -> list:
    """
    Query state with filters (implements FR3: Dapr State)
    
    Args:
        store: State store name
        query: Query filter (Dapr query syntax)
    
    Returns:
        List of matching state items
    """
    url = f"{DAPR_BASE}/state/{store}/query"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=query)
            response.raise_for_status()
            return response.json().get("results", [])
    except Exception as e:
        logger.error(f"Failed to query state: {e}", exc_info=True)
        return []
'''


def generate_models_py() -> str:
    """Generate models.py with Pydantic models"""
    
    return '''"""
Pydantic Models
Data validation models for requests/responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class QueryRequest(BaseModel):
    """User query request"""
    user_id: str = Field(..., description="User identifier")
    query: str = Field(..., description="User query text")
    context: Optional[Dict[str, Any]] = None


class ConceptRequest(BaseModel):
    """Concept explanation request"""
    user_id: str
    concept: str = Field(..., description="Concept to explain")
    difficulty: int = Field(5, ge=1, le=10, description="Difficulty level")


class DebugRequest(BaseModel):
    """Debug request"""
    user_id: str
    code: str = Field(..., description="Code with error")
    error: str = Field(..., description="Error message")
    language: str = Field("python", description="Programming language")


class ExerciseRequest(BaseModel):
    """Exercise generation request"""
    user_id: str
    concept: str = Field(..., description="Concept to practice")
    difficulty: int = Field(5, ge=1, le=10)


class ProgressRequest(BaseModel):
    """Progress analysis request"""
    user_id: str
    timeframe_days: int = Field(7, ge=1, description="Analysis timeframe")


class AgentResponse(BaseModel):
    """Generic agent response"""
    agent: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
'''


def generate_requirements_txt() -> str:
    """Generate requirements.txt (section 4.1: Dependencies)"""
    
    return '''fastapi==0.109.0
uvicorn[standard]==0.27.0
dapr==1.12.0
pydantic==2.5.3
pydantic-settings==2.1.0
openai==1.10.0
httpx==0.26.0
python-json-logger==2.0.7
'''


def generate_dockerfile() -> str:
    """Generate Dockerfile (section 4.2: Dockerfile Template)"""
    
    return '''FROM python:3.11-slim

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
HEALTHCHECK --interval=30s --timeout=3s \\
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''


def generate_k8s_deployment(agent_name: str) -> str:
    """Generate Kubernetes deployment (FR5: Kubernetes Deployment)"""
    
    return f'''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {agent_name}-agent
  labels:
    app: {agent_name}-agent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {agent_name}-agent
  template:
    metadata:
      labels:
        app: {agent_name}-agent
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "{agent_name}-agent"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
    spec:
      containers:
      - name: {agent_name}
        image: {agent_name}-agent:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: AGENT_NAME
          value: "{agent_name}"
        - name: DAPR_HTTP_PORT
          value: "3500"
        - name: PUBSUB_NAME
          value: "kafka-pubsub"
        - name: STATE_STORE
          value: "postgres-state"
        - name: LLM_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-secrets
              key: api-key
        - name: LLM_MODEL
          value: "gpt-4"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: {agent_name}-agent
  labels:
    app: {agent_name}-agent
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: {agent_name}-agent
'''


def generate_agent(agent_name: str, output_dir: Path):
    """Generate complete agent service (implements FR1-FR5)"""
    
    if agent_name not in AGENT_CONFIGS:
        print(f"Error: Unknown agent '{agent_name}'")
        print(f"Valid agents: {', '.join(AGENT_CONFIGS.keys())}")
        sys.exit(1)
    
    config = AGENT_CONFIGS[agent_name]
    
    # Create directory structure
    agent_dir = output_dir / agent_name
    app_dir = agent_dir / "app"
    k8s_dir = agent_dir / "k8s"
    
    app_dir.mkdir(parents=True, exist_ok=True)
    k8s_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating {agent_name} agent...")
    
    # Generate files
    files = {
        app_dir / "__init__.py": "",
        app_dir / "main.py": generate_main_py(agent_name, config),
        app_dir / "config.py": generate_config_py(),
        app_dir / "models.py": generate_models_py(),
        app_dir / "agent.py": generate_agent_py(agent_name, config),
        app_dir / "dapr_client.py": generate_dapr_client_py(),
        agent_dir / "requirements.txt": generate_requirements_txt(),
        agent_dir / "Dockerfile": generate_dockerfile(),
        agent_dir / ".env.example": "LLM_API_KEY=your-api-key\nLLM_MODEL=gpt-4\n",
        k8s_dir / "deployment.yaml": generate_k8s_deployment(agent_name),
    }
    
    for filepath, content in files.items():
        filepath.write_text(content)
        print(f"  ✓ {filepath.relative_to(output_dir)}")
    
    print(f"\n✅ {agent_name.capitalize()} agent generated successfully!")
    print(f"   Location: {agent_dir}")
    print(f"   Files: {len(files)}")
    print(f"\nNext steps:")
    print(f"1. cd {agent_name}")
    print(f"2. cp .env.example .env && edit .env")
    print(f"3. docker build -t {agent_name}-agent .")
    print(f"4. kubectl apply -f k8s/")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_agent.py <agent_name>")
        print(f"\nAvailable agents: {', '.join(AGENT_CONFIGS.keys())}")
        sys.exit(1)
    
    agent_name = sys.argv[1].lower()
    output_dir = Path.cwd()
    
    generate_agent(agent_name, output_dir)
