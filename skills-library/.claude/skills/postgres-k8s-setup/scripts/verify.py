#!/usr/bin/env python3
"""
PostgreSQL Health Verification
Implements FR4: Health Verification
"""

import subprocess
import sys


def run_command(cmd):
    """Execute shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"


def check_pod_running():
    """Verify PostgreSQL pod is in Running state"""
    cmd = "kubectl get pods -n postgres -l app=postgres -o jsonpath='{.items[0].status.phase}'"
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode != 0:
        print(f"✗ Failed to get pod status: {stderr}")
        return False
    
    if stdout.strip() == "Running":
        print("✓ PostgreSQL pod is Running")
        return True
    else:
        print(f"✗ PostgreSQL pod is not Running (current state: {stdout.strip()})")
        return False


def check_database_connection():
    """Verify PostgreSQL accepts connections and learnflow database exists"""
    cmd = """kubectl exec -n postgres postgres-0 -- psql -U learnflow_user -d learnflow -c "SELECT 1" """
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode != 0:
        print(f"✗ Database connection failed: {stderr}")
        return False
    
    print("✓ PostgreSQL accepts connections")
    return True


def check_schema_initialized():
    """Verify LearnFlow tables exist"""
    cmd = """kubectl exec -n postgres postgres-0 -- psql -U learnflow_user -d learnflow -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" """
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode != 0:
        print(f"✗ Schema check failed: {stderr}")
        return False
    
    table_count = int(stdout.strip())
    if table_count >= 5:
        print(f"✓ LearnFlow schema initialized ({table_count} tables)")
        return True
    else:
        print(f"✗ Schema not fully initialized (found {table_count} tables, expected 5+)")
        return False


def main():
    """Run all health checks"""
    print("🔍 Verifying PostgreSQL deployment...")
    print()
    
    checks = [
        check_pod_running(),
        check_database_connection(),
        check_schema_initialized()
    ]
    
    print()
    if all(checks):
        print("✅ PostgreSQL is healthy and ready")
        sys.exit(0)
    else:
        print("❌ PostgreSQL health check failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
