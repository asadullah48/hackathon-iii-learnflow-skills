# LearnFlow Documentation Deployment

Deploy LearnFlow documentation to Kubernetes using Docusaurus.

## Quick Start
```bash
# 1. Copy templates to your Docusaurus project
cp Dockerfile /path/to/docusaurus/
cp nginx.conf /path/to/docusaurus/
cp -r k8s/ /path/to/docusaurus/
cp scripts/deploy.sh /path/to/docusaurus/

# 2. Deploy to Kubernetes
cd /path/to/docusaurus
bash deploy.sh
```

## Configuration

### Dockerfile
Multi-stage build for optimized image size:
- Stage 1: Node.js build (npm run build)
- Stage 2: Nginx serving (alpine base)

### Nginx
Production-ready configuration:
- Gzip compression
- Static asset caching (1 year)
- SPA fallback routing
- Health check endpoint

### Kubernetes
Minimal resource deployment:
- 1 replica (can scale with HPA)
- 32Mi-64Mi memory
- 50m-100m CPU
- Health probes

## Access

After deployment:
```bash
# Get service URL (Minikube)
minikube service learnflow-docs --url

# Add to /etc/hosts
echo "$(minikube ip) docs.learnflow.local" | sudo tee -a /etc/hosts

# Access documentation
open http://docs.learnflow.local
```

## Versioning

Enable versioning in Docusaurus:
```bash
npm run docusaurus docs:version 1.0.0
```

Versions appear in dropdown automatically.
