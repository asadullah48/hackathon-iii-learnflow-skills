# Kubernetes Foundation - Reference Documentation

## Architecture Overview

Provides core Kubernetes operations for managing resources across all LearnFlow microservices.
````
┌───────────────────────────────────────────────────┐
│  Kubernetes Cluster                               │
│  ┌─────────────────┐  ┌─────────────────┐        │
│  │  Namespaces     │  │  Resources      │        │
│  │  - learnflow    │  │  - Pods         │        │
│  │  - kafka        │  │  - Deployments  │        │
│  │  - postgres     │  │  - Services     │        │
│  │  - dapr-system  │  │  - ConfigMaps   │        │
│  └─────────────────┘  └─────────────────┘        │
└───────────────────────────────────────────────────┘
````

## Script Reference

### 1. k8s_get.sh - Resource Queries
````bash
./scripts/k8s_get.sh <resource> [namespace] [name]
````

**Examples:**
````bash
# List all pods in learnflow namespace
./scripts/k8s_get.sh pods learnflow

# Get specific deployment
./scripts/k8s_get.sh deployment learnflow triage-agent

# List all services across all namespaces
./scripts/k8s_get.sh services

# Get node information
./scripts/k8s_get.sh nodes
````

**Supported Resources:**
- `pods`, `po`
- `deployments`, `deploy`
- `services`, `svc`
- `configmaps`, `cm`
- `secrets`
- `ingress`, `ing`
- `persistentvolumeclaims`, `pvc`
- `nodes`
- `namespaces`, `ns`

**Output Format:**
````
NAME                    READY   STATUS    RESTARTS   AGE
triage-agent-abc123     2/2     Running   0          5m
concepts-agent-def456   2/2     Running   0          5m
````

### 2. k8s_logs.sh - Container Logs
````bash
./scripts/k8s_logs.sh <pod-name> [namespace] [container] [--follow] [--tail=N]
````

**Examples:**
````bash
# Get logs from main container
./scripts/k8s_logs.sh triage-agent-abc123 learnflow

# Get Dapr sidecar logs
./scripts/k8s_logs.sh triage-agent-abc123 learnflow daprd

# Follow logs in real-time
./scripts/k8s_logs.sh triage-agent-abc123 learnflow --follow

# Last 100 lines
./scripts/k8s_logs.sh triage-agent-abc123 learnflow --tail=100

# Stream both containers
./scripts/k8s_logs.sh triage-agent-abc123 learnflow --all-containers --follow
````

**Log Filtering:**
````bash
# Find errors
./scripts/k8s_logs.sh triage-agent-abc123 learnflow | grep ERROR

# Search for user ID
./scripts/k8s_logs.sh triage-agent-abc123 learnflow | grep "user_id=12345"

# Export to file
./scripts/k8s_logs.sh triage-agent-abc123 learnflow > debug.log
````

### 3. k8s_describe.sh - Resource Details
````bash
./scripts/k8s_describe.sh <resource-type> <name> [namespace]
````

**Examples:**
````bash
# Describe pod (includes events)
./scripts/k8s_describe.sh pod triage-agent-abc123 learnflow

# Describe deployment
./scripts/k8s_describe.sh deployment triage-agent learnflow

# Describe service
./scripts/k8s_describe.sh service triage-agent learnflow

# Describe node
./scripts/k8s_describe.sh node minikube
````

**Use Cases:**
- Pod startup failures → Check Events section
- Image pull errors → Check Container section
- Resource limits → Check Limits/Requests
- Network issues → Check Endpoints

### 4. k8s_exec.sh - Container Commands
````bash
./scripts/k8s_exec.sh <pod-name> <command> [namespace] [container]
````

**Examples:**
````bash
# Interactive shell
./scripts/k8s_exec.sh triage-agent-abc123 "bash" learnflow

# Check Python version
./scripts/k8s_exec.sh triage-agent-abc123 "python --version" learnflow

# Test Dapr connectivity
./scripts/k8s_exec.sh triage-agent-abc123 "curl http://localhost:3500/v1.0/healthz" learnflow

# View environment variables
./scripts/k8s_exec.sh triage-agent-abc123 "env" learnflow

# Test database connection
./scripts/k8s_exec.sh triage-agent-abc123 "nc -zv postgres 5432" learnflow
````

**Debugging Scenarios:**

**DNS Resolution:**
````bash
./scripts/k8s_exec.sh triage-agent-abc123 "nslookup kafka.kafka.svc.cluster.local" learnflow
````

**Network Connectivity:**
````bash
./scripts/k8s_exec.sh triage-agent-abc123 "curl -v http://concepts-agent:5000/health" learnflow
````

**File System Check:**
````bash
./scripts/k8s_exec.sh triage-agent-abc123 "ls -la /app" learnflow
````

### 5. k8s_apply.sh - Resource Deployment
````bash
./scripts/k8s_apply.sh <yaml-file> [namespace]
````

**Examples:**
````bash
# Apply single file
./scripts/k8s_apply.sh deployment.yaml learnflow

# Apply directory
./scripts/k8s_apply.sh ./k8s/ learnflow

# Dry-run (validate only)
./scripts/k8s_apply.sh deployment.yaml learnflow --dry-run

# Force replacement
./scripts/k8s_apply.sh deployment.yaml learnflow --force
````

**Deployment Workflow:**
````bash
# 1. Validate syntax
kubectl apply -f deployment.yaml --dry-run=client

# 2. Apply with script
./scripts/k8s_apply.sh deployment.yaml learnflow

# 3. Watch rollout
kubectl rollout status deployment/triage-agent -n learnflow

# 4. Verify pods
./scripts/k8s_get.sh pods learnflow
````

## Advanced Operations

### Resource Monitoring
````bash
# Watch pod status
watch -n 2 "./scripts/k8s_get.sh pods learnflow"

# Monitor resource usage
kubectl top pods -n learnflow
kubectl top nodes

# Check HPA status
kubectl get hpa -n learnflow
````

### Debugging Workflows

**Pod Not Starting:**
````bash
# 1. Check pod status
./scripts/k8s_get.sh pods learnflow

# 2. Describe pod for events
./scripts/k8s_describe.sh pod {pod-name} learnflow

# 3. Check logs
./scripts/k8s_logs.sh {pod-name} learnflow

# 4. Check image pull
./scripts/k8s_describe.sh pod {pod-name} learnflow | grep -A5 "Events:"
````

**Service Not Reachable:**
````bash
# 1. Verify service exists
./scripts/k8s_get.sh service triage-agent learnflow

# 2. Check endpoints
kubectl get endpoints triage-agent -n learnflow

# 3. Test from another pod
./scripts/k8s_exec.sh debug-pod "curl http://triage-agent:5000/health" learnflow

# 4. Check network policies
kubectl get networkpolicies -n learnflow
````

**ConfigMap/Secret Issues:**
````bash
# 1. List resources
./scripts/k8s_get.sh configmap learnflow

# 2. View content
kubectl get configmap nextjs-config -n learnflow -o yaml

# 3. Check if mounted
./scripts/k8s_describe.sh pod {pod-name} learnflow | grep -A10 "Mounts:"

# 4. Verify in container
./scripts/k8s_exec.sh {pod-name} "cat /etc/config/app.conf" learnflow
````

## Namespace Management

### Create Namespaces
````bash
kubectl create namespace learnflow
kubectl create namespace kafka
kubectl create namespace postgres

# Label namespaces
kubectl label namespace learnflow name=learnflow
kubectl label namespace kafka name=kafka
kubectl label namespace postgres name=postgres
````

### Resource Quotas
````yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: learnflow-quota
  namespace: learnflow
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    persistentvolumeclaims: "10"
    pods: "50"
````

### Network Policies
````yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-learnflow-agents
  namespace: learnflow
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/part-of: learnflow
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: learnflow
````

## Troubleshooting

### Common Issues

**ImagePullBackOff:**
````bash
# Symptom: Pod status shows ImagePullBackOff
./scripts/k8s_describe.sh pod {pod-name} learnflow

# Solutions:
# 1. Check image name and tag
# 2. Verify registry credentials
kubectl create secret docker-registry regcred \
  --docker-server=<registry> \
  --docker-username=<user> \
  --docker-password=<pass>

# 3. For Minikube, load image
minikube image load myimage:latest
````

**CrashLoopBackOff:**
````bash
# Symptom: Pod restarts repeatedly
./scripts/k8s_logs.sh {pod-name} learnflow --previous

# Check exit code
./scripts/k8s_describe.sh pod {pod-name} learnflow | grep "Exit Code"

# Common causes:
# - Application error on startup
# - Missing dependencies
# - Port already in use
# - Failed health check
````

**Pending Pods:**
````bash
# Symptom: Pod stuck in Pending state
./scripts/k8s_describe.sh pod {pod-name} learnflow

# Check events for:
# - Insufficient CPU/memory
# - PVC not bound
# - Node selector not matched
# - Taints/tolerations mismatch
````

### Resource Cleanup

**Delete Resources:**
````bash
# Delete specific pod
kubectl delete pod {pod-name} -n learnflow

# Delete deployment (removes all pods)
kubectl delete deployment triage-agent -n learnflow

# Delete namespace (removes everything)
kubectl delete namespace learnflow

# Force delete stuck pod
kubectl delete pod {pod-name} -n learnflow --force --grace-period=0
````

**Reset Deployment:**
````bash
# Scale to zero
kubectl scale deployment triage-agent --replicas=0 -n learnflow

# Scale back up
kubectl scale deployment triage-agent --replicas=3 -n learnflow
````

## Performance Optimization

### Resource Limits
````yaml
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
````

### Pod Priority
````yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000
globalDefault: false
description: "High priority for critical services"
````

### Affinity Rules
````yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchLabels:
          app: triage-agent
      topologyKey: kubernetes.io/hostname
````

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Debugging Pods](https://kubernetes.io/docs/tasks/debug/debug-application/)
- [Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
