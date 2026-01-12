# nextjs-k8s-deploy Skill Specification

**Version:** 1.0.0  
**Status:** Draft  
**Owner:** Asadullah (asadullah48)  
**Created:** 2026-01-12  
**Hackathon:** Panaversity Hackathon III - LearnFlow Frontend

---

## 1. Overview

### 1.1 Purpose
Deploy Next.js applications to Kubernetes with production optimizations, environment configuration, and Dapr integration for LearnFlow frontend.

### 1.2 Scope
**In Scope:**
- Next.js production build and optimization
- Multi-stage Dockerfile for minimal image size
- Kubernetes deployment with ingress
- Environment variable configuration
- Static asset serving (CDN-ready)
- Dapr service invocation for backend APIs
- Health/readiness probes
- Auto-scaling configuration

**Out of Scope:**
- Next.js application code (user provides)
- Database migrations (handled by postgres-k8s-setup)
- Backend services (handled by fastapi-dapr-agent)

### 1.3 Token Budget
- **SKILL.md:** ≤150 tokens
- **Scripts:** 0 tokens (external files)
- **Results:** ≤40 tokens (deployment status)
- **Total:** ≤190 tokens per invocation

### 1.4 Success Metrics
- **Autonomy:** 90% (minimal user input required)
- **Efficiency:** 94% (template-based deployment)
- **Cross-agent compatibility:** 100% (standard K8s patterns)

---

## 2. User Stories

### US1: Deploy LearnFlow Frontend
**As a** hackathon participant  
**I want** to deploy the Next.js frontend to Kubernetes  
**So that** users can access the LearnFlow learning platform

**Acceptance Criteria:**
- Production-optimized build (minified, tree-shaken)
- Docker image ≤150MB (multi-stage build)
- Kubernetes deployment with 2 replicas
- Ingress configured for external access
- Environment variables for API endpoints

### US2: Configure Environment Variables
**As a** developer  
**I want** to configure API endpoints and secrets  
**So that** the frontend can communicate with backend services

**Acceptance Criteria:**
- ConfigMap for non-sensitive config
- Secrets for API keys
- Dapr app-id references for service invocation
- Support for multiple environments (dev/prod)

### US3: Enable Auto-Scaling
**As a** platform operator  
**I want** horizontal pod autoscaling  
**So that** the frontend scales with user traffic

**Acceptance Criteria:**
- HPA based on CPU (target: 70%)
- Min replicas: 2, Max replicas: 10
- Scale-up/down policies configured

---

## 3. Functional Requirements

### FR1: Multi-Stage Dockerfile
**Description:** Build optimized Next.js production image

**Template:**
````dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Runtime
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs
EXPOSE 3000
ENV PORT 3000

CMD ["node", "server.js"]
````

**Outputs:**
- Optimized image ≤150MB
- Non-root user (nextjs:1001)
- Standalone output mode

### FR2: Kubernetes Deployment
**Description:** Deploy with Dapr annotations and resource limits

**Template:**
````yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: learnflow-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: learnflow-frontend
  template:
    metadata:
      labels:
        app: learnflow-frontend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "learnflow-frontend"
        dapr.io/app-port: "3000"
    spec:
      containers:
      - name: frontend
        image: learnflow-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "http://localhost:3500/v1.0/invoke"
        - name: DAPR_HTTP_PORT
          value: "3500"
        envFrom:
        - configMapRef:
            name: frontend-config
        - secretRef:
            name: frontend-secrets
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 10
````

### FR3: Service & Ingress
**Description:** Expose frontend via LoadBalancer or Ingress

**Service Template:**
````yaml
apiVersion: v1
kind: Service
metadata:
  name: learnflow-frontend
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 3000
  selector:
    app: learnflow-frontend
````

**Ingress Template:**
````yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: learnflow-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: learnflow.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: learnflow-frontend
            port:
              number: 80
````

### FR4: ConfigMap & Secrets
**Description:** Environment configuration management

**ConfigMap:**
````yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-config
data:
  NEXT_PUBLIC_APP_NAME: "LearnFlow"
  TRIAGE_AGENT_ID: "triage-agent"
  CONCEPTS_AGENT_ID: "concepts-agent"
  DEBUG_AGENT_ID: "debug-agent"
  EXERCISE_AGENT_ID: "exercise-agent"
  PROGRESS_AGENT_ID: "progress-agent"
````

**Secret Template:**
````yaml
apiVersion: v1
kind: Secret
metadata:
  name: frontend-secrets
type: Opaque
stringData:
  NEXT_PUBLIC_SUPABASE_URL: "your-supabase-url"
  NEXT_PUBLIC_SUPABASE_ANON_KEY: "your-anon-key"
````

### FR5: Horizontal Pod Autoscaler
**Description:** Auto-scale based on CPU usage

**HPA Template:**
````yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: learnflow-frontend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: learnflow-frontend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 2
        periodSeconds: 30
      selectPolicy: Max
````

---

## 4. Technical Requirements

### 4.1 Next.js Configuration
**next.config.js adjustments:**
````javascript
module.exports = {
  output: 'standalone', // For Docker deployment
  compress: true,       // Gzip compression
  poweredByHeader: false,
  images: {
    unoptimized: true,  // Or configure external CDN
  },
  env: {
    DAPR_HTTP_PORT: process.env.DAPR_HTTP_PORT || '3500',
  }
}
````

### 4.2 Health Endpoint
**pages/api/health.ts:**
````typescript
import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  // Basic health check
  res.status(200).json({ 
    status: 'healthy',
    timestamp: new Date().toISOString()
  })
}
````

### 4.3 Dapr Service Invocation
**Example API call to backend:**
````typescript
const DAPR_URL = `http://localhost:${process.env.DAPR_HTTP_PORT}/v1.0/invoke`

async function callTriageAgent(query: string) {
  const response = await fetch(
    `${DAPR_URL}/triage-agent/method/triage`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    }
  )
  return response.json()
}
````

### 4.4 Build Script
**package.json scripts:**
````json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "docker:build": "docker build -t learnflow-frontend .",
    "k8s:deploy": "kubectl apply -f k8s/"
  }
}
````

---

## 5. Deployment Script

### 5.1 deploy.sh
**Purpose:** Automate build and deployment
````bash
#!/bin/bash
set -e

NAMESPACE="${NAMESPACE:-default}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "🚀 Deploying LearnFlow Frontend to Kubernetes"

# Build Docker image
echo "📦 Building Docker image..."
docker build -t learnflow-frontend:$IMAGE_TAG .

# Load to Minikube (if using)
if command -v minikube &> /dev/null; then
    echo "📤 Loading image to Minikube..."
    minikube image load learnflow-frontend:$IMAGE_TAG
fi

# Create namespace if needed
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply Kubernetes manifests
echo "☸️  Applying Kubernetes manifests..."
kubectl apply -f k8s/ -n $NAMESPACE

# Wait for deployment
echo "⏳ Waiting for deployment..."
kubectl rollout status deployment/learnflow-frontend -n $NAMESPACE --timeout=5m

# Get service URL
echo "✅ Deployment complete!"
if command -v minikube &> /dev/null; then
    echo "🌐 Access at: $(minikube service learnflow-frontend --url -n $NAMESPACE)"
else
    echo "🌐 Service: kubectl get svc learnflow-frontend -n $NAMESPACE"
fi
````

---

## 6. Testing Plan

### 6.1 Build Tests
- Docker build completes successfully
- Image size ≤150MB
- No vulnerabilities (trivy scan)

### 6.2 Deployment Tests
- Pods reach Running state
- Health endpoints return 200
- Dapr sidecar injected correctly
- Environment variables loaded

### 6.3 Integration Tests
- Frontend can call Triage agent via Dapr
- Static assets served correctly
- Page load time <2s

---

## 7. SKILL.md Content
````markdown
# nextjs-k8s-deploy

Deploy Next.js applications to Kubernetes with production optimizations.

## Usage
```bash
# Deploy LearnFlow frontend
bash scripts/deploy.sh

# Custom image tag
IMAGE_TAG=v1.0.0 bash scripts/deploy.sh

# Custom namespace
NAMESPACE=production bash scripts/deploy.sh
```

## Features

- **Multi-stage build**: Optimized Docker image ≤150MB
- **Dapr integration**: Service-to-service invocation
- **Auto-scaling**: HPA based on CPU (2-10 replicas)
- **Health checks**: Liveness/readiness probes
- **Production-ready**: Standalone output, compression

## Configuration

Edit `k8s/configmap.yaml` and `k8s/secret.yaml` before deploying.

Required secrets:
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

## Token Usage

- SKILL.md: ~145 tokens
- Scripts: External (0 tokens)
- Results: ~35 tokens
````

---

## 8. Acceptance Criteria

**Skill complete when:**
- ✅ Dockerfile builds image ≤150MB
- ✅ Deployment succeeds in Minikube
- ✅ Health endpoints return 200
- ✅ Dapr service invocation works
- ✅ HPA configured and functional
- ✅ Token budget ≤190 tokens

---

**End of Specification**
