# postgres-k8s-setup

Deploy PostgreSQL on Kubernetes with automated schema initialization, migrations, and connection management for LearnFlow application.

## When to Use

- Deploy PostgreSQL for LearnFlow backend services
- Initialize LearnFlow database schema (users, progress, struggles, exercises, executions)
- Apply database schema migrations
- Verify PostgreSQL health and readiness
- Get database connection details for services

## Instructions

### 1. Deploy PostgreSQL

```bash
# Development (ephemeral storage, 512Mi)
bash scripts/deploy.sh dev

# Production (persistent storage, 2Gi)
bash scripts/deploy.sh prod
```

### 2. Apply Database Migrations

```bash
# Execute all pending migrations from migrations/ directory
bash scripts/apply_migrations.sh
```

### 3. Verify Deployment

```bash
# Check PostgreSQL health and connectivity
python scripts/verify.py
```

### 4. Get Connection String

```bash
# Retrieve connection details for LearnFlow services
python scripts/get_connection.py
```

## Outputs

- PostgreSQL StatefulSet deployed to `postgres` namespace
- LearnFlow schema initialized (5 tables with indexes)
- Database ready for services to connect
- Connection string: `postgresql://learnflow_user:password@postgres.postgres.svc.cluster.local:5432/learnflow`

## Configuration

**Development:**
- 1 replica, 512Mi memory, 500m CPU
- Ephemeral storage (emptyDir)
- Simple password in environment

**Production:**
- 1 replica, 2Gi memory, 1 CPU
- Persistent volume (10Gi PVC)
- Kubernetes Secrets for credentials
