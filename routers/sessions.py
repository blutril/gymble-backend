from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional
import models
import schemas
from database import get_db
from datetime import datetime
from utils.stats import WorkoutAnalytics
from utils.auth import get_current_user
import json

router = APIRouter()

@router.post("/", response_model=schemas.WorkoutSession, status_code=status.HTTP_201_CREATED)
def create_session(
    session: schemas.WorkoutSessionCreate, 
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
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
            notes=session.notes,
            session_rpe=session.session_rpe,
            user_readiness=session.user_readiness
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.get("/", response_model=List[schemas.WorkoutSession])
def get_sessions(
    user_id: int = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    sessions = db.query(models.WorkoutSession).options(
        selectinload(models.WorkoutSession.exercises).selectinload(models.SessionExercise.exercise),
        selectinload(models.WorkoutSession.workout)
    ).filter(
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
    try:
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
        if session_update.session_rpe is not None:
            db_session.session_rpe = session_update.session_rpe
        if session_update.user_readiness is not None:
            db_session.user_readiness = session_update.user_readiness
        if session_update.training_load is not None:
            db_session.training_load = session_update.training_load
        if session_update.total_volume is not None:
            db_session.total_volume = session_update.total_volume
        
        # Add exercises if provided
        if session_update.exercises:
            for exercise_data in session_update.exercises:
                try:
                    exercise_dict = exercise_data.dict()
                    # Remove any fields that don't exist in the model
                    valid_fields = {
                        'exercise_id', 'sets_completed', 'reps_completed', 'weight',
                        'sets_data', 'time_under_tension', 'total_volume', 
                        'best_set_weight', 'best_set_reps', 'avg_rpe', 'notes'
                    }
                    filtered_dict = {k: v for k, v in exercise_dict.items() if k in valid_fields}
                    
                    db_session_exercise = models.SessionExercise(
                        session_id=session_id,
                        **filtered_dict
                    )
                    db.add(db_session_exercise)
                except Exception as e:
                    db.rollback()
                    print(f"Error adding exercise: {e}")
                    raise HTTPException(status_code=400, detail=f"Error adding exercise: {str(e)}")
        
        db.commit()
        db.refresh(db_session)
        return db_session
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error updating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")

@router.post("/{session_id}/complete", response_model=schemas.WorkoutSession)
def complete_session(session_id: int, db: Session = Depends(get_db)):
    try:
        db_session = db.query(models.WorkoutSession).options(
            selectinload(models.WorkoutSession.exercises).selectinload(models.SessionExercise.exercise),
            selectinload(models.WorkoutSession.workout)
        ).filter(
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
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        print(f"Error completing session: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to complete session: {str(e)}")

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

# Advanced endpoints

@router.get("/{session_id}/metrics", status_code=status.HTTP_200_OK)
def get_session_metrics(session_id: int, db: Session = Depends(get_db)):
    """Get advanced metrics for a session (1RM, volume, etc.)"""
    db_session = db.query(models.WorkoutSession).filter(
        models.WorkoutSession.id == session_id
    ).first()
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    metrics = {
        'session_id': db_session.id,
        'duration': db_session.duration_minutes,
        'session_rpe': db_session.session_rpe,
        'training_load': db_session.training_load,
        'total_volume': db_session.total_volume,
        'user_readiness': db_session.user_readiness,
        'exercises': []
    }
    
    for exercise in db_session.exercises:
        sets_data = WorkoutAnalytics.parse_sets_data(exercise.sets_data)
        best_set = WorkoutAnalytics.get_best_set(sets_data)
        
        exercise_metrics = {
            'exercise_id': exercise.exercise_id,
            'exercise_name': exercise.exercise.name,
            'sets_completed': exercise.sets_completed,
            'reps_completed': exercise.reps_completed,
            'total_volume': exercise.total_volume,
            'time_under_tension': exercise.time_under_tension,
            'avg_rpe': exercise.avg_rpe,
            'best_set': best_set,
            'estimated_1rm': WorkoutAnalytics.calculate_one_rm_brzycki(
                best_set['weight'], best_set['reps']
            ) if best_set else None
        }
        metrics['exercises'].append(exercise_metrics)
    
    return metrics

@router.get("/user/{user_id}/prs", status_code=status.HTTP_200_OK)
def get_user_prs(user_id: int, db: Session = Depends(get_db)):
    """Get all personal records for a user across exercises"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all unique exercises the user has trained
    exercises = db.query(models.Exercise).join(
        models.SessionExercise
    ).join(
        models.WorkoutSession
    ).filter(
        models.WorkoutSession.user_id == user_id
    ).distinct().all()
    
    prs = {}
    for exercise in exercises:
        pr_summary = WorkoutAnalytics.get_exercise_pr_summary(db, user_id, exercise.id)
        prs[exercise.name] = pr_summary
    
    return prs

@router.get("/user/{user_id}/strength-trends", status_code=status.HTTP_200_OK)
def get_strength_trends(
    user_id: int,
    exercise_id: Optional[int] = None,
    days: int = 90,
    db: Session = Depends(get_db)
):
    """Get strength progression trends"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # If specific exercise not provided, get all exercises
    if exercise_id:
        trend = WorkoutAnalytics.get_strength_trend(db, user_id, exercise_id, days)
        return {'exercise_id': exercise_id, 'trend': trend}
    
    exercises = db.query(models.Exercise).join(
        models.SessionExercise
    ).join(
        models.WorkoutSession
    ).filter(
        models.WorkoutSession.user_id == user_id
    ).distinct().all()
    
    trends = {}
    for exercise in exercises:
        trend = WorkoutAnalytics.get_strength_trend(db, user_id, exercise.id, days)
        if trend:
            trends[exercise.name] = trend
    
    return trends

@router.get("/user/{user_id}/volume-trends", status_code=status.HTTP_200_OK)
def get_volume_trends(
    user_id: int,
    muscle_group: Optional[str] = None,
    days: int = 90,
    db: Session = Depends(get_db)
):
    """Get volume progression trends"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    trend = WorkoutAnalytics.get_volume_trend(db, user_id, muscle_group, days)
    return {'muscle_group': muscle_group, 'trend': trend}

@router.get("/user/{user_id}/weekly-stats", status_code=status.HTTP_200_OK)
def get_weekly_stats(
    user_id: int,
    weeks: int = 4,
    db: Session = Depends(get_db)
):
    """Get weekly training load, monotony, strain, and readiness"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    stats = WorkoutAnalytics.get_weekly_stats(db, user_id, weeks)
    return {
        'user_id': user_id,
        'weeks': stats
    }
