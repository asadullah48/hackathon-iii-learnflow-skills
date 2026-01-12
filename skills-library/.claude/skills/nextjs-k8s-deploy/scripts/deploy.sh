#!/bin/bash
# Implements section 5.1 from nextjs-k8s-deploy_SPEC.md
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
