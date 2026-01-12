# docusaurus-deploy

Deploy Docusaurus documentation sites to Kubernetes.

## Usage
```bash
# Deploy documentation
bash scripts/deploy.sh

# Custom image tag
IMAGE_TAG=v1.0.0 bash scripts/deploy.sh

# Custom namespace
NAMESPACE=production bash scripts/deploy.sh
```

## Features

- **Lightweight**: Nginx-based serving (≤20MB image)
- **Fast**: Static site with optimized caching
- **Versioned**: Multi-version documentation support
- **Production-ready**: Gzip, cache headers, health checks

## Configuration

Place templates in your Docusaurus project:
```bash
cp Dockerfile /path/to/docusaurus/
cp nginx.conf /path/to/docusaurus/
cp -r k8s/ /path/to/docusaurus/
```

## Token Usage

- SKILL.md: ~115 tokens
- Scripts: External (0 tokens)
- Results: ~28 tokens
