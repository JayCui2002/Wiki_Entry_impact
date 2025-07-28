"""
Database Reset Script (Fixed Version)
This script drops all tables and recreates them based on the current models.
WARNING: This will delete all data in the database.
"""

import asyncio
import os
import sys
from sqlalchemy import text

# Add backend directory to sys.path to allow for absolute imports
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Now that the path is set, we can import from the application
from app.core.database import engine, Base
from app.models import contributor, user, analysis_session

async def reset_database():
    """
    Drops all tables and recreates them.
    """
    print("--- Database Reset Script (Fixed Version) ---")
    print("WARNING: This script will drop all tables and delete all existing data.")
    
    try:
        confirm = input("Are you sure you want to continue? (y/n): ")
        if confirm.lower() != 'y':
            print("Database reset cancelled.")
            return

        print("\nConnecting to database and dropping all tables...")
        async with engine.begin() as conn:
            # Drop tables in the correct order to avoid foreign key constraint issues
            await conn.execute(text("DROP TABLE IF EXISTS contributors CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS analysis_sessions CASCADE")) 
            await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        print("All tables dropped successfully.")

        print("\nCreating all tables based on current models...")
        # The Base object knows about all models that inherit from it,
        # so we only need to call create_all once.
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("All tables created successfully.")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        await engine.dispose()
        print("\nDatabase connection closed. Reset process finished.")

if __name__ == "__main__":
    asyncio.run(reset_database()) 