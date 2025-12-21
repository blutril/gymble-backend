from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
import models
import schemas
from database import get_db
from utils.auth import get_current_user

router = APIRouter()

def add_last_session_date(workout: models.Workout, db: Session):
    """Add the last session date to a workout object"""
    last_session = db.query(models.WorkoutSession).filter(
        models.WorkoutSession.workout_id == workout.id
    ).order_by(desc(models.WorkoutSession.started_at)).first()
    
    workout.last_session_date = last_session.started_at if last_session else None
    return workout

@router.post("/", response_model=schemas.Workout, status_code=status.HTTP_201_CREATED)
def create_workout(
    workout: schemas.WorkoutCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if workout.plan_id is not None:
        plan = db.query(models.WorkoutPlan).filter(
            models.WorkoutPlan.id == workout.plan_id,
            models.WorkoutPlan.user_id == user_id
        ).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Workout plan not found")
    
    # Create workout
    db_workout = models.Workout(
        user_id=user_id,
        plan_id=workout.plan_id,
        name=workout.name,
        description=workout.description,
        icon=workout.icon,
        category=workout.category
    )
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    
    # Add exercises to workout
    for index, exercise_data in enumerate(workout.exercises):
        exercise_dict = exercise_data.dict()
        # If order is not provided, use the index
        if exercise_dict.get('order') is None:
            exercise_dict['order'] = index
        db_workout_exercise = models.WorkoutExercise(
            workout_id=db_workout.id,
            **exercise_dict
        )
        db.add(db_workout_exercise)
    
    db.commit()
    db.refresh(db_workout)
    return db_workout

@router.get("/", response_model=List[schemas.Workout])
def get_workouts(
    user_id: int = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    workouts = db.query(models.Workout).filter(
        models.Workout.user_id == user_id
    ).offset(skip).limit(limit).all()
    
    # Add last session date to each workout
    for workout in workouts:
        add_last_session_date(workout, db)
    
    return workouts

@router.get("/{workout_id}", response_model=schemas.Workout)
def get_workout(workout_id: int, db: Session = Depends(get_db)):
    workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    # Add last session date
    add_last_session_date(workout, db)
    
    return workout

@router.put("/{workout_id}", response_model=schemas.Workout)
def update_workout(
    workout_id: int, 
    workout: schemas.WorkoutCreate, 
    db: Session = Depends(get_db)
):
    db_workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")

    if workout.plan_id is not None:
        plan = db.query(models.WorkoutPlan).filter(
            models.WorkoutPlan.id == workout.plan_id,
            models.WorkoutPlan.user_id == db_workout.user_id
        ).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Workout plan not found")
    
    db_workout.name = workout.name
    db_workout.description = workout.description
    db_workout.plan_id = workout.plan_id
    db_workout.icon = workout.icon
    db_workout.category = workout.category
    
    # Delete existing exercises
    db.query(models.WorkoutExercise).filter(
        models.WorkoutExercise.workout_id == workout_id
    ).delete()
    
    # Add new exercises
    for index, exercise_data in enumerate(workout.exercises):
        exercise_dict = exercise_data.dict()
        # If order is not provided, use the index
        if exercise_dict.get('order') is None:
            exercise_dict['order'] = index
        db_workout_exercise = models.WorkoutExercise(
            workout_id=workout_id,
            **exercise_dict
        )
        db.add(db_workout_exercise)
    
    db.commit()
    db.refresh(db_workout)
    return db_workout

@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    db_workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    db.delete(db_workout)
    db.commit()
    return None
