#!/bin/bash
set -e

# Database Migration Runner
# Implements FR3: Database Migration Support

echo "🔄 Applying database migrations..."

# Connection details
DB_HOST="postgres.postgres.svc.cluster.local"
DB_PORT="5432"
DB_NAME="learnflow"
DB_USER="learnflow_user"
DB_PASS="dev_password_change_in_prod"

export PGPASSWORD="$DB_PASS"

# Create schema_migrations table if not exists
kubectl exec -n postgres postgres-0 -- psql -U "$DB_USER" -d "$DB_NAME" <<'EOF'
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
EOF

# Get list of migration files
MIGRATIONS_DIR="$(dirname "$0")/../migrations"
if [ ! -d "$MIGRATIONS_DIR" ]; then
    echo "⚠️  No migrations directory found"
    exit 0
fi

MIGRATION_FILES=$(find "$MIGRATIONS_DIR" -name "*.sql" -type f | sort)

if [ -z "$MIGRATION_FILES" ]; then
    echo "✅ No migration files to apply"
    exit 0
fi

# Apply each migration
for MIGRATION_FILE in $MIGRATION_FILES; do
    FILENAME=$(basename "$MIGRATION_FILE")
    VERSION=$(echo "$FILENAME" | grep -o '^[0-9]\+')
    
    # Check if already applied
    APPLIED=$(kubectl exec -n postgres postgres-0 -- psql -U "$DB_USER" -d "$DB_NAME" -t -c \
        "SELECT COUNT(*) FROM schema_migrations WHERE version = $VERSION;")
    
    if [ "$APPLIED" -gt 0 ]; then
        echo "⏭️  Migration $FILENAME already applied"
        continue
    fi
    
    echo "📝 Applying migration: $FILENAME"
    
    # Apply migration in transaction
    kubectl exec -i -n postgres postgres-0 -- psql -U "$DB_USER" -d "$DB_NAME" <<MIGRATION
BEGIN;

-- Apply migration
$(cat "$MIGRATION_FILE")

-- Record migration
INSERT INTO schema_migrations (version) VALUES ($VERSION);

COMMIT;
MIGRATION
    
    if [ $? -eq 0 ]; then
        echo "✅ Migration $FILENAME applied successfully"
    else
        echo "❌ Migration $FILENAME failed"
        exit 1
    fi
done

echo "✅ All migrations applied successfully"

# Show applied migrations
echo ""
echo "📊 Applied migrations:"
kubectl exec -n postgres postgres-0 -- psql -U "$DB_USER" -d "$DB_NAME" -c \
    "SELECT version, applied_at FROM schema_migrations ORDER BY version;"
