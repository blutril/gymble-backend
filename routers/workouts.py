from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Workout, status_code=status.HTTP_201_CREATED)
def create_workout(workout: schemas.WorkoutCreate, user_id: int, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create workout
    db_workout = models.Workout(
        user_id=user_id,
        name=workout.name,
        description=workout.description
    )
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    
    # Add exercises to workout
    for exercise_data in workout.exercises:
        db_workout_exercise = models.WorkoutExercise(
            workout_id=db_workout.id,
            **exercise_data.dict()
        )
        db.add(db_workout_exercise)
    
    db.commit()
    db.refresh(db_workout)
    return db_workout

@router.get("/", response_model=List[schemas.Workout])
def get_workouts(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    workouts = db.query(models.Workout).filter(
        models.Workout.user_id == user_id
    ).offset(skip).limit(limit).all()
    return workouts

@router.get("/{workout_id}", response_model=schemas.Workout)
def get_workout(workout_id: int, db: Session = Depends(get_db)):
    workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
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
    
    db_workout.name = workout.name
    db_workout.description = workout.description
    
    # Delete existing exercises
    db.query(models.WorkoutExercise).filter(
        models.WorkoutExercise.workout_id == workout_id
    ).delete()
    
    # Add new exercises
    for exercise_data in workout.exercises:
        db_workout_exercise = models.WorkoutExercise(
            workout_id=workout_id,
            **exercise_data.dict()
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
