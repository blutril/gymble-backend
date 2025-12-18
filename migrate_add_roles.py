"""
Migration script to:
1. Add role field to existing users (set to 'member' by default)
2. Create a default admin user (admin/admin123)
3. Set patrick user as admin if it exists
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal, engine, Base
import models
from passlib.context import CryptContext
from datetime import datetime, timezone

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def migrate():
    db = SessionLocal()
    try:
        print("Starting migration...")
        
        # Step 1: Set all existing users without a role to 'member' using raw SQL
        with engine.connect() as connection:
            # First, let's check the current default
            update_query = text("""
                UPDATE users SET role = 'member' WHERE role IS NULL
            """)
            result = connection.execute(update_query)
            connection.commit()
            print(f"✓ Updated existing users to 'member' role")
        
        # Step 2: Create default admin user if it doesn't exist using raw SQL
        with engine.connect() as connection:
            check_admin = text("""
                SELECT id FROM users WHERE email = 'admin@gymble.com'
            """)
            result = connection.execute(check_admin).fetchone()
            
            if not result:
                hashed_pw = get_password_hash("admin123")
                insert_admin = text("""
                    INSERT INTO users (username, email, full_name, hashed_password, role, created_at)
                    VALUES (:username, :email, :full_name, :password, :role, :created_at)
                """)
                connection.execute(insert_admin, {
                    'username': 'admin',
                    'email': 'admin@gymble.com',
                    'full_name': 'Admin User',
                    'password': hashed_pw,
                    'role': 'admin',
                    'created_at': datetime.now(timezone.utc)
                })
                connection.commit()
                print("✓ Created default admin user (email: admin@gymble.com, password: admin123)")
            else:
                print("ℹ Default admin user already exists")
        
        # Step 3: Set patrick as admin if the user exists using raw SQL
        with engine.connect() as connection:
            check_patrick = text("""
                SELECT id, role FROM users WHERE username = 'patrick'
            """)
            patrick_result = connection.execute(check_patrick).fetchone()
            
            if patrick_result:
                if patrick_result[1] != 'admin':
                    update_patrick = text("""
                        UPDATE users SET role = 'admin' WHERE username = 'patrick'
                    """)
                    connection.execute(update_patrick)
                    connection.commit()
                    print(f"✓ Set user 'patrick' as admin")
                else:
                    print("ℹ User 'patrick' is already an admin")
            else:
                print("ℹ User 'patrick' does not exist yet")
        
        print("\n✓ Migration completed successfully!")
        print("\nAdmin Users:")
        with engine.connect() as connection:
            admin_users_query = text("""
                SELECT username, email FROM users WHERE role = 'admin'
            """)
            admin_users = connection.execute(admin_users_query).fetchall()
            for admin in admin_users:
                print(f"  - {admin[0]} ({admin[1]})")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
