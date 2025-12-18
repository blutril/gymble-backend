"""
Migration script to add user_id column to exercises table.
This makes all existing exercises as built-in exercises (user_id = NULL).
"""

from sqlalchemy import inspect, text
from database import engine, Base
import models

def migrate():
    # Check if column already exists
    inspector = inspect(engine)
    columns = inspector.get_columns('exercises')
    column_names = [c['name'] for c in columns]
    
    if 'user_id' not in column_names:
        print("Adding user_id column to exercises table...")
        with engine.connect() as connection:
            # Add user_id column with NULL default (all existing exercises are built-in)
            connection.execute(text("""
                ALTER TABLE exercises
                ADD COLUMN user_id INTEGER REFERENCES users(id)
            """))
            connection.commit()
            print("✓ user_id column added successfully!")
    else:
        print("user_id column already exists")

if __name__ == "__main__":
    migrate()
