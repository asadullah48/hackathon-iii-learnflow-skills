#!/bin/bash
# Implements FR5: Deployment Script

set -e

# Configuration
NAMESPACE="${NAMESPACE:-default}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
IMAGE_NAME="learnflow-docs"

echo "📚 Deploying LearnFlow Documentation to Kubernetes"
echo "   Namespace: $NAMESPACE"
echo "   Image: $IMAGE_NAME:$IMAGE_TAG"

# Build Docker image
echo ""
echo "🔨 Building Docker image..."
docker build -t $IMAGE_NAME:$IMAGE_TAG .

# Load to Minikube if available
if command -v minikube &> /dev/null && minikube status &> /dev/null; then
    echo "📦 Loading image to Minikube..."
    minikube image load $IMAGE_NAME:$IMAGE_TAG
fi

# Create namespace if it doesn't exist
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply Kubernetes manifests
echo "☸️  Applying Kubernetes manifests..."
kubectl apply -f k8s/ -n $NAMESPACE

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."
kubectl rollout status deployment/learnflow-docs -n $NAMESPACE --timeout=3m

# Get service information
echo ""
echo "✅ Documentation deployed successfully!"
echo ""
echo "📊 Deployment Status:"
kubectl get deployment learnflow-docs -n $NAMESPACE
echo ""
echo "🌐 Service Information:"
kubectl get service learnflow-docs -n $NAMESPACE

# Get access URL for Minikube
if command -v minikube &> /dev/null && minikube status &> /dev/null; then
    echo ""
    echo "🔗 Access URL:"
    minikube service learnflow-docs --url -n $NAMESPACE
    echo ""
    echo "💡 Add to /etc/hosts:"
    echo "   $(minikube ip) docs.learnflow.local"
fi
