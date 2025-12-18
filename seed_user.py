from database import SessionLocal
import models
import bcrypt

def seed_user():
    db = SessionLocal()
    
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.username == "demo_user").first()
    if existing_user:
        print(f"User already exists with ID: {existing_user.id}")
        db.close()
        return
    
    # Create demo user with bcrypt hashing
    password = "demo123"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    user = models.User(
        username="demo_user",
        email="demo@gymble.com",
        full_name="Demo User",
        hashed_password=hashed_password
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"Demo user created successfully with ID: {user.id}")
    print(f"Username: demo_user")
    print(f"Email: demo@gymble.com")
    
    db.close()

if __name__ == "__main__":
    seed_user()
