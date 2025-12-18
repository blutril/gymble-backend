"""
Direct SQL migration to add role column to users table
Run this to add the role column to the existing database
"""

from sqlalchemy import text
from database import engine

def add_role_column():
    """Add role column to users table"""
    with engine.connect() as connection:
        try:
            # Check if column exists
            check_column = text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name='users' AND column_name='role'
            """)
            result = connection.execute(check_column).fetchone()
            
            if result:
                print("✓ Role column already exists")
                return
            
            # Create enum type if it doesn't exist
            create_enum = text("""
                DO $$ BEGIN
                    CREATE TYPE user_role AS ENUM ('admin', 'member');
                EXCEPTION WHEN duplicate_object THEN null;
                END $$;
            """)
            connection.execute(create_enum)
            print("✓ Created user_role enum type (or it already existed)")
            
            # Add role column with default value
            add_column = text("""
                ALTER TABLE users 
                ADD COLUMN role user_role DEFAULT 'member'
            """)
            connection.execute(add_column)
            connection.commit()
            print("✓ Added role column to users table with default value 'member'")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            connection.rollback()
            raise

if __name__ == "__main__":
    print("Adding role column to users table...")
    add_role_column()
    print("\n✓ Database migration completed successfully!")
