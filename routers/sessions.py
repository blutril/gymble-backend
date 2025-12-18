from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import get_db
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=schemas.WorkoutSession, status_code=status.HTTP_201_CREATED)
def create_session(
    session: schemas.WorkoutSessionCreate, 
    user_id: int, 
    db: Session = Depends(get_db)
):
    # Check if user and workout exist
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    workout = db.query(models.Workout).filter(models.Workout.id == session.workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    # Create session
    db_session = models.WorkoutSession(
        user_id=user_id,
        workout_id=session.workout_id,
        notes=session.notes
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/", response_model=List[schemas.WorkoutSession])
def get_sessions(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sessions = db.query(models.WorkoutSession).filter(
        models.WorkoutSession.user_id == user_id
    ).order_by(models.WorkoutSession.started_at.desc()).offset(skip).limit(limit).all()
    return sessions

@router.get("/{session_id}", response_model=schemas.WorkoutSession)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.WorkoutSession).filter(
        models.WorkoutSession.id == session_id
    ).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.put("/{session_id}", response_model=schemas.WorkoutSession)
def update_session(
    session_id: int, 
    session_update: schemas.WorkoutSessionUpdate, 
    db: Session = Depends(get_db)
):
    db_session = db.query(models.WorkoutSession).filter(
        models.WorkoutSession.id == session_id
    ).first()
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update session fields
    if session_update.completed_at is not None:
        db_session.completed_at = session_update.completed_at
    if session_update.duration_minutes is not None:
        db_session.duration_minutes = session_update.duration_minutes
    if session_update.notes is not None:
        db_session.notes = session_update.notes
    
    # Add exercises if provided
    if session_update.exercises:
        for exercise_data in session_update.exercises:
            db_session_exercise = models.SessionExercise(
                session_id=session_id,
                **exercise_data.dict()
            )
            db.add(db_session_exercise)
    
    db.commit()
    db.refresh(db_session)
    return db_session

@router.post("/{session_id}/complete", response_model=schemas.WorkoutSession)
def complete_session(session_id: int, db: Session = Depends(get_db)):
    db_session = db.query(models.WorkoutSession).filter(
        models.WorkoutSession.id == session_id
    ).first()
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db_session.completed_at = datetime.utcnow()
    if db_session.started_at:
        duration = (db_session.completed_at - db_session.started_at).total_seconds() / 60
        db_session.duration_minutes = int(duration)
    
    db.commit()
    db.refresh(db_session)
    return db_session

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    db_session = db.query(models.WorkoutSession).filter(
        models.WorkoutSession.id == session_id
    ).first()
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(db_session)
    db.commit()
    return None
