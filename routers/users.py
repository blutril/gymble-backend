from fastapi import APIRouter, Depends, HTTPException, status
from starlette.requests import Request
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import get_db
from passlib.context import CryptContext
from utils.auth import create_access_token, verify_token

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Generate token
    access_token = create_access_token(
        data={"user_id": db_user.id, "email": db_user.email}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }

@router.post("/login", response_model=schemas.Token)
def login_user(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login user with email and password"""
    # Find user by email
    db_user = db.query(models.User).filter(models.User.email == user_login.email).first()
    if not db_user or not verify_password(user_login.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate token
    access_token = create_access_token(
        data={"user_id": db_user.id, "email": db_user.email}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }

@router.get("/me", response_model=schemas.User)
def get_current_user_profile(request: Request, db: Session = Depends(get_db)):
    """Get current user profile"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header.split(" ")[1]
    token_data = verify_token(token)
    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/me", response_model=schemas.User)
def update_user_profile(
    user_update: dict,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header.split(" ")[1]
    token_data = verify_token(token)
    
    db_user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update allowed fields
    update_fields = ["full_name", "age", "height", "weight", "bio", "profile_picture"]
    for field, value in user_update.items():
        if field in update_fields and value is not None:
            setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user (legacy endpoint)"""
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[schemas.User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: dict, db: Session = Depends(get_db)):
    """Update user by ID (admin endpoint)"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update allowed fields
    update_fields = ["username", "email", "full_name", "age", "height", "weight", "bio", "profile_picture"]
    for field, value in user_update.items():
        if field in update_fields and value is not None:
            if field == "username" or field == "email":
                # Check for duplicates
                existing = db.query(models.User).filter(
                    getattr(models.User, field) == value,
                    models.User.id != user_id
                ).first()
                if existing:
                    raise HTTPException(status_code=400, detail=f"{field} already taken")
            setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user by ID (admin endpoint)"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete related data
    db.query(models.WorkoutSession).filter(models.WorkoutSession.user_id == user_id).delete()
    db.query(models.Workout).filter(models.Workout.user_id == user_id).delete()
    db.query(models.WorkoutPlan).filter(models.WorkoutPlan.user_id == user_id).delete()
    
    db.delete(db_user)
    db.commit()
    return None

@router.get("/{user_id}/stats", response_model=dict)
def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    """Get user statistics"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    total_workouts = db.query(models.Workout).filter(models.Workout.user_id == user_id).count()
    total_sessions = db.query(models.WorkoutSession).filter(models.WorkoutSession.user_id == user_id).count()
    completed_sessions = db.query(models.WorkoutSession).filter(
        models.WorkoutSession.user_id == user_id,
        models.WorkoutSession.completed_at.isnot(None)
    ).count()
    
    total_plans = db.query(models.WorkoutPlan).filter(models.WorkoutPlan.user_id == user_id).count()
    
    return {
        "user_id": user_id,
        "username": db_user.username,
        "total_workouts": total_workouts,
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "total_workout_plans": total_plans,
    }


