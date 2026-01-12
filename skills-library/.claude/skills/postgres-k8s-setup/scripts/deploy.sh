#!/bin/bash
set -e

# PostgreSQL Kubernetes Deployment Script
# Implements FR1: Environment-Aware Deployment

ENV="${1:-dev}"

echo "🚀 Deploying PostgreSQL (${ENV} mode)..."

# Set resource limits based on environment
if [ "$ENV" = "prod" ]; then
    REPLICAS=1
    MEMORY="2Gi"
    CPU="1"
    STORAGE_CLASS="standard"
    PVC_SIZE="10Gi"
    USE_PVC=true
else
    REPLICAS=1
    MEMORY="512Mi"
    CPU="500m"
    USE_PVC=false
fi

# Create namespace
kubectl create namespace postgres --dry-run=client -o yaml | kubectl apply -f -

# Create ConfigMap with init schema
kubectl create configmap postgres-init-schema \
    --from-file=init-schema.sql=scripts/init_schema.sql \
    --namespace=postgres \
    --dry-run=client -o yaml | kubectl apply -f -

# Create Secret (prod only)
if [ "$ENV" = "prod" ]; then
    echo "⚠️  For production, create Secret manually:"
    echo "kubectl create secret generic postgres-credentials \\"
    echo "  --from-literal=username=learnflow_user \\"
    echo "  --from-literal=password=YOUR_STRONG_PASSWORD \\"
    echo "  -n postgres"
    echo ""
fi

# Create PVC (prod only)
if [ "$USE_PVC" = true ]; then
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data
  namespace: postgres
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: ${STORAGE_CLASS}
  resources:
    requests:
      storage: ${PVC_SIZE}
EOF
fi

# Deploy StatefulSet
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: postgres
spec:
  serviceName: postgres
  replicas: ${REPLICAS}
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      initContainers:
      - name: init-schema
        image: postgres:16-alpine
        command:
        - sh
        - -c
        - |
          if [ ! -f /var/lib/postgresql/data/schema_initialized ]; then
            echo "Initializing schema..."
            cp /init-schema/init-schema.sql /docker-entrypoint-initdb.d/
            touch /var/lib/postgresql/data/schema_initialized
          else
            echo "Schema already initialized"
          fi
        volumeMounts:
        - name: init-schema
          mountPath: /init-schema
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
      containers:
      - name: postgres
        image: postgres:16-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: learnflow
        - name: POSTGRES_USER
          value: learnflow_user
        - name: POSTGRES_PASSWORD
          value: dev_password_change_in_prod
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        resources:
          requests:
            memory: ${MEMORY}
            cpu: ${CPU}
          limits:
            memory: ${MEMORY}
            cpu: ${CPU}
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
        - name: init-schema
          mountPath: /docker-entrypoint-initdb.d
      volumes:
      - name: init-schema
        configMap:
          name: postgres-init-schema
      - name: postgres-data
$(if [ "$USE_PVC" = true ]; then
cat <<PVCVOL
        persistentVolumeClaim:
          claimName: postgres-data
PVCVOL
else
cat <<EMPTYVOL
        emptyDir: {}
EMPTYVOL
fi)
EOF

# Deploy Service
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: postgres
spec:
  type: ClusterIP
  ports:
  - port: 5432
    targetPort: 5432
  selector:
    app: postgres
EOF

echo "⏳ Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n postgres --timeout=120s

echo "✅ PostgreSQL deployed successfully (${ENV} mode)"
echo "📊 Resources: ${REPLICAS} replica, ${MEMORY} memory, ${CPU} CPU"
echo "💾 Storage: $([ "$USE_PVC" = true ] && echo "Persistent (${PVC_SIZE})" || echo "Ephemeral")"
