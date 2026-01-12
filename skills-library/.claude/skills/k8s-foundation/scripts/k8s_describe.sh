#!/bin/bash
# Describe Kubernetes resource
# Implements FR3: Resource Description

set -e

TYPE="$1"
NAME="$2"
NAMESPACE="$3"

if [ -z "$TYPE" ] || [ -z "$NAME" ] || [ -z "$NAMESPACE" ]; then
    echo "❌ Usage: k8s_describe.sh <type> <name> <namespace>"
    echo ""
    echo "Examples:"
    echo "  bash scripts/k8s_describe.sh pod postgres-0 postgres"
    echo "  bash scripts/k8s_describe.sh deployment triage-service learnflow"
    echo "  bash scripts/k8s_describe.sh service postgres postgres"
    exit 1
fi

echo "🔍 Describing $TYPE/$NAME in namespace: $NAMESPACE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

kubectl describe "$TYPE" "$NAME" -n "$NAMESPACE" 2>&1

EXIT_CODE=$?

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $EXIT_CODE -ne 0 ]; then
    echo "❌ Failed to describe $TYPE/$NAME"
    echo "💡 Tip: Check if resource exists and namespace is correct"
    exit 1
fi

echo "✅ Description complete"
