from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Exercise Schemas
class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    muscle_group: str
    equipment: str
    difficulty: str
    instructions: Optional[str] = None

class ExerciseCreate(ExerciseBase):
    pass

class Exercise(ExerciseBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Workout Exercise Schemas
class WorkoutExerciseBase(BaseModel):
    exercise_id: int
    sets: int
    reps: int
    rest_seconds: int
    order: int

class WorkoutExerciseCreate(WorkoutExerciseBase):
    pass

class WorkoutExercise(WorkoutExerciseBase):
    id: int
    exercise: Exercise
    
    class Config:
        from_attributes = True

# Workout Schemas
class WorkoutBase(BaseModel):
    name: str
    description: Optional[str] = None

class WorkoutCreate(WorkoutBase):
    exercises: List[WorkoutExerciseCreate] = []

class Workout(WorkoutBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    exercises: List[WorkoutExercise] = []
    
    class Config:
        from_attributes = True

# Session Exercise Schemas
class SessionExerciseBase(BaseModel):
    exercise_id: int
    sets_completed: int
    reps_completed: int
    weight: float
    notes: Optional[str] = None

class SessionExerciseCreate(SessionExerciseBase):
    pass

class SessionExercise(SessionExerciseBase):
    id: int
    exercise: Exercise
    
    class Config:
        from_attributes = True

# Workout Session Schemas
class WorkoutSessionBase(BaseModel):
    workout_id: int
    notes: Optional[str] = None

class WorkoutSessionCreate(WorkoutSessionBase):
    pass

class WorkoutSessionUpdate(BaseModel):
    completed_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    exercises: Optional[List[SessionExerciseCreate]] = None

class WorkoutSession(WorkoutSessionBase):
    id: int
    user_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    workout: Workout
    exercises: List[SessionExercise] = []
    
    class Config:
        from_attributes = True
