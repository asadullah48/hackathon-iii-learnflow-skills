# LearnFlow Frontend Deployment

This directory contains Kubernetes manifests and Docker configuration for deploying the LearnFlow Next.js frontend.

## Quick Start

1. **Copy templates to your Next.js project:**
```bash
   cp Dockerfile /path/to/your/nextjs-app/
   cp -r k8s/ /path/to/your/nextjs-app/
   cp next.config.example.js /path/to/your/nextjs-app/next.config.js
```

2. **Configure secrets:**
```bash
   # Edit k8s/secret.yaml with your actual values
   nano k8s/secret.yaml
```

3. **Deploy:**
```bash
   cd /path/to/your/nextjs-app
   bash /path/to/skills/scripts/deploy.sh
```

## Files

- `Dockerfile`: Multi-stage build for optimized image
- `k8s/deployment.yaml`: K8s deployment with Dapr annotations
- `k8s/service.yaml`: ClusterIP service
- `k8s/ingress.yaml`: Ingress for external access
- `k8s/configmap.yaml`: Non-sensitive configuration
- `k8s/secret.yaml`: Sensitive credentials
- `k8s/hpa.yaml`: Horizontal Pod Autoscaler
- `next.config.example.js`: Next.js configuration
- `health.ts.example`: Health check endpoint
- `dapr-client.ts.example`: Dapr service invocation utilities
