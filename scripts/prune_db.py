import os
import sys
import django
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / 'apps'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UniCart.settings')
django.setup()

from django.db import connection

def prune():
    with connection.cursor() as cursor:
        # 1. Find all marketplace tables
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'marketplace_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        if not tables:
            print("No marketplace tables found to prune.")
            return

        print(f"Found {len(tables)} tables to remove: {', '.join(tables)}")
        
        # 2. Drop them
        for table in tables:
            print(f"Dropping table: {table}...")
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        
        print("\nPruning complete! Your database is now clean.")

if __name__ == "__main__":
    prune()
