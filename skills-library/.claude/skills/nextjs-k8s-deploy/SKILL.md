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
