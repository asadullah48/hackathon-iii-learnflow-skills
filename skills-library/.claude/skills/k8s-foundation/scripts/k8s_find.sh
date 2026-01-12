#!/bin/bash
# Find resources across all namespaces
# Implements FR5: Multi-Namespace Search

set -e

TYPE="$1"
PATTERN="${2:-.*}"

if [ -z "$TYPE" ]; then
    echo "❌ Usage: k8s_find.sh <type> [pattern]"
    echo ""
    echo "Examples:"
    echo "  bash scripts/k8s_find.sh pods"
    echo "  bash scripts/k8s_find.sh services postgres"
    echo "  bash scripts/k8s_find.sh deployments triage"
    exit 1
fi

echo "🔎 Searching for $TYPE matching pattern: $PATTERN"
echo ""

kubectl get "$TYPE" -A 2>&1 | grep -E "NAMESPACE|$PATTERN" || {
    echo ""
    echo "⚠️  No $TYPE found matching pattern: $PATTERN"
    exit 0
}

echo ""
echo "✅ Search complete"
