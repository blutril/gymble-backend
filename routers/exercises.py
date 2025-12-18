from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import models
import schemas
from database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Exercise, status_code=status.HTTP_201_CREATED)
def create_exercise(exercise: schemas.ExerciseCreate, db: Session = Depends(get_db)):
    db_exercise = models.Exercise(**exercise.dict())
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

@router.get("/", response_model=List[schemas.Exercise])
def get_exercises(
    skip: int = 0, 
    limit: int = 100,
    muscle_group: Optional[str] = None,
    equipment: Optional[str] = None,
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Exercise)
    
    if muscle_group:
        query = query.filter(models.Exercise.muscle_group == muscle_group)
    if equipment:
        query = query.filter(models.Exercise.equipment == equipment)
    if difficulty:
        query = query.filter(models.Exercise.difficulty == difficulty)
    
    exercises = query.offset(skip).limit(limit).all()
    return exercises

@router.get("/{exercise_id}", response_model=schemas.Exercise)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    exercise = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise

@router.put("/{exercise_id}", response_model=schemas.Exercise)
def update_exercise(
    exercise_id: int, 
    exercise: schemas.ExerciseCreate, 
    db: Session = Depends(get_db)
):
    db_exercise = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    for key, value in exercise.dict().items():
        setattr(db_exercise, key, value)
    
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(exercise_id: int, db: Session = Depends(get_db)):
    db_exercise = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    db.delete(db_exercise)
    db.commit()
    return None
