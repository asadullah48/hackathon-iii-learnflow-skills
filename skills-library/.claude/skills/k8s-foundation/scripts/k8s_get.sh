#!/bin/bash
# Get Kubernetes resources with optimized output
# Implements FR1: Resource Listing

set -e

TYPE="${1:-pods}"
NAMESPACE="${2:--A}"  # -A for all namespaces by default

echo "📋 Getting $TYPE $([ "$NAMESPACE" = "-A" ] && echo "across all namespaces" || echo "in namespace: $NAMESPACE")"
echo ""

if [ "$NAMESPACE" = "-A" ]; then
    kubectl get "$TYPE" -A -o wide
else
    kubectl get "$TYPE" -n "$NAMESPACE" -o wide
fi

EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ Failed to get $TYPE"
    echo "💡 Tip: Check if the resource type is valid and cluster is accessible"
    exit 1
fi

echo ""
echo "✅ Resource listing complete"
