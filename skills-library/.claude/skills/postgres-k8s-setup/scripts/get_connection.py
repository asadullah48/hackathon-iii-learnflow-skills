#!/usr/bin/env python3
"""
PostgreSQL Connection String Retrieval
Implements FR5: Connection String Retrieval
"""


def main():
    """Return PostgreSQL connection details for LearnFlow services"""
    
    # Connection details
    host = "postgres.postgres.svc.cluster.local"
    port = 5432
    database = "learnflow"
    user = "learnflow_user"
    password = "dev_password_change_in_prod"
    
    # Print connection details
    print("=" * 70)
    print("PostgreSQL Connection Details")
    print("=" * 70)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Database: {database}")
    print(f"User: {user}")
    print(f"Password: {password}")
    print()
    print("Connection String:")
    print(f"postgresql://{user}:{password}@{host}:{port}/{database}")
    print("=" * 70)
    print()
    print("Usage Examples:")
    print()
    print("# Python (asyncpg)")
    print(f'conn = await asyncpg.connect("{host}", port={port}, user="{user}", password="{password}", database="{database}")')
    print()
    print("# Python (psycopg2)")
    print(f'conn = psycopg2.connect(host="{host}", port={port}, user="{user}", password="{password}", database="{database}")')
    print()
    print("# Environment Variable")
    print(f'export DATABASE_URL="postgresql://{user}:{password}@{host}:{port}/{database}"')
    print("=" * 70)


if __name__ == "__main__":
    main()
