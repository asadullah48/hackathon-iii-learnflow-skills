#!/bin/bash
# Delete Kubernetes resource
# Implements FR4: Resource Deletion

set -e

TYPE="$1"
NAME="$2"
NAMESPACE="$3"

if [ -z "$TYPE" ] || [ -z "$NAME" ] || [ -z "$NAMESPACE" ]; then
    echo "❌ Usage: k8s_delete.sh <type> <name> <namespace>"
    echo ""
    echo "Examples:"
    echo "  bash scripts/k8s_delete.sh pod stuck-pod default"
    echo "  bash scripts/k8s_delete.sh deployment old-deployment learnflow"
    exit 1
fi

echo "⚠️  WARNING: Deleting $TYPE/$NAME in namespace $NAMESPACE"
echo ""

kubectl delete "$TYPE" "$NAME" -n "$NAMESPACE" 2>&1

EXIT_CODE=$?

echo ""

if [ $EXIT_CODE -ne 0 ]; then
    echo "❌ Failed to delete $TYPE/$NAME"
    echo "💡 Tip: Check if resource exists and you have permissions"
    exit 1
fi

echo "✅ Resource deleted successfully"
