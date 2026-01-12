#!/bin/bash
# Retrieve pod logs
# Implements FR2: Log Retrieval

set -e

POD="$1"
NAMESPACE="$2"
LINES="${3:-50}"

if [ -z "$POD" ] || [ -z "$NAMESPACE" ]; then
    echo "❌ Usage: k8s_logs.sh <pod> <namespace> [lines]"
    echo ""
    echo "Examples:"
    echo "  bash scripts/k8s_logs.sh postgres-0 postgres"
    echo "  bash scripts/k8s_logs.sh postgres-0 postgres 100"
    exit 1
fi

echo "📜 Retrieving last $LINES lines from pod: $POD (namespace: $NAMESPACE)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

kubectl logs "$POD" -n "$NAMESPACE" --tail="$LINES" 2>&1

EXIT_CODE=$?

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $EXIT_CODE -ne 0 ]; then
    echo "❌ Failed to retrieve logs from $POD"
    echo "💡 Tip: Check if pod exists and is running"
    exit 1
fi

echo "✅ Log retrieval complete"
