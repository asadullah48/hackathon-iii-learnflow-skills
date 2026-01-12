# k8s-foundation

Essential Kubernetes operations with zero-token overhead for AI agent workflows.

## When to Use

- Check pod, service, or deployment status
- Retrieve application logs for debugging
- Describe Kubernetes resources in detail
- Clean up failed or stuck deployments
- Search for resources across namespaces

## Instructions

### 1. Get Resources

```bash
# Get all pods across all namespaces
bash scripts/k8s_get.sh pods

# Get pods in specific namespace
bash scripts/k8s_get.sh pods postgres

# Get services, deployments, etc.
bash scripts/k8s_get.sh services
bash scripts/k8s_get.sh deployments learnflow
```

### 2. Tail Logs

```bash
# Get last 50 lines (default)
bash scripts/k8s_logs.sh postgres-0 postgres

# Get last 100 lines
bash scripts/k8s_logs.sh postgres-0 postgres 100

# Stream logs (follow)
bash scripts/k8s_logs.sh triage-service-abc123 learnflow 20
```

### 3. Describe Resource

```bash
# Describe pod
bash scripts/k8s_describe.sh pod postgres-0 postgres

# Describe deployment
bash scripts/k8s_describe.sh deployment triage-service learnflow

# Describe service
bash scripts/k8s_describe.sh service postgres postgres
```

### 4. Delete Resource

```bash
# Delete pod
bash scripts/k8s_delete.sh pod stuck-pod-name default

# Delete deployment
bash scripts/k8s_delete.sh deployment old-deployment learnflow
```

### 5. Find Resources

```bash
# Find all resources of a type
bash scripts/k8s_find.sh pods

# Find resources matching pattern
bash scripts/k8s_find.sh services postgres
bash scripts/k8s_find.sh deployments triage
```

## Outputs

- **Get**: Formatted table with NAME, NAMESPACE, STATUS, AGE
- **Logs**: Last N lines of pod logs
- **Describe**: Detailed resource information
- **Delete**: Confirmation of deletion
- **Find**: Resources matching search pattern across all namespaces

## Common Use Cases

**Debugging LearnFlow Services:**
```bash
# Check all LearnFlow pods
bash scripts/k8s_get.sh pods learnflow

# Get logs from triage service
bash scripts/k8s_logs.sh triage-service-xyz learnflow 100

# Describe failing pod
bash scripts/k8s_describe.sh pod triage-service-xyz learnflow
```

**Checking PostgreSQL:**
```bash
bash scripts/k8s_get.sh pods postgres
bash scripts/k8s_logs.sh postgres-0 postgres 50
bash scripts/k8s_describe.sh statefulset postgres postgres
```
