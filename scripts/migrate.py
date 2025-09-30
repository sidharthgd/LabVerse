#!/usr/bin/env python3
"""
Alembic migration helpers
"""

import subprocess
import sys
from pathlib import Path

def run_migration(command: str):
    """Run Alembic migration command"""
    try:
        result = subprocess.run(
            ["alembic", command],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✓ Migration {command} completed successfully")
            print(result.stdout)
        else:
            print(f"✗ Migration {command} failed")
            print(result.stderr)
            sys.exit(1)
            
    except FileNotFoundError:
        print("Error: Alembic not found. Please install it with: pip install alembic")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python migrate.py <command>")
        print("Commands: upgrade, downgrade, revision, current, history")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "upgrade":
        run_migration("upgrade head")
    elif command == "downgrade":
        run_migration("downgrade -1")
    elif command == "revision":
        message = sys.argv[2] if len(sys.argv) > 2 else "Auto migration"
        run_migration(f'revision --autogenerate -m "{message}"')
    elif command == "current":
        run_migration("current")
    elif command == "history":
        run_migration("history")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
