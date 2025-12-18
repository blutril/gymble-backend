"""
Migration script to add new user profile columns
Run this script to update your existing database with the new columns
"""
from sqlalchemy import text
from database import engine

def migrate():
    """Add missing columns to users table"""
    with engine.connect() as connection:
        # Check if columns exist before adding them
        try:
            # Add age column
            connection.execute(text("ALTER TABLE users ADD COLUMN age INTEGER NULL"))
            print("✓ Added age column")
        except Exception as e:
            print(f"✗ age column: {e}")
        
        try:
            # Add height column
            connection.execute(text("ALTER TABLE users ADD COLUMN height FLOAT NULL"))
            print("✓ Added height column")
        except Exception as e:
            print(f"✗ height column: {e}")
        
        try:
            # Add weight column
            connection.execute(text("ALTER TABLE users ADD COLUMN weight FLOAT NULL"))
            print("✓ Added weight column")
        except Exception as e:
            print(f"✗ weight column: {e}")
        
        try:
            # Add bio column
            connection.execute(text("ALTER TABLE users ADD COLUMN bio TEXT NULL"))
            print("✓ Added bio column")
        except Exception as e:
            print(f"✗ bio column: {e}")
        
        try:
            # Add profile_picture column
            connection.execute(text("ALTER TABLE users ADD COLUMN profile_picture VARCHAR NULL"))
            print("✓ Added profile_picture column")
        except Exception as e:
            print(f"✗ profile_picture column: {e}")
        
        connection.commit()
        print("\nMigration complete!")

if __name__ == "__main__":
    print("Starting migration...\n")
    migrate()
