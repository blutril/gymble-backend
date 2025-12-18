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
    order: Optional[int] = None

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
    plan_id: Optional[int] = None
    icon: str = "fitness"  # Icon name for the workout

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


class WorkoutPlanBase(BaseModel):
    name: str
    description: Optional[str] = None


class WorkoutPlanCreate(WorkoutPlanBase):
    workout_ids: List[int] = []


class WorkoutPlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    workout_ids: Optional[List[int]] = None


class WorkoutPlan(WorkoutPlanBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    workouts: List[Workout] = []

    class Config:
        from_attributes = True

# Session Exercise Schemas
class SetData(BaseModel):
    """Per-set metrics data"""
    weight: float
    reps: int
    rpe: Optional[float] = None  # Rate of Perceived Exertion (1-10)
    rir: Optional[float] = None  # Reps in Reserve
    tut: Optional[float] = None  # Time Under Tension in seconds
    rest_after: Optional[int] = None  # Rest after set in seconds

class SessionExerciseBase(BaseModel):
    exercise_id: int
    sets_completed: int
    reps_completed: int
    weight: float
    notes: Optional[str] = None
    sets_data: Optional[List[SetData]] = None
    time_under_tension: Optional[float] = None
    total_volume: Optional[float] = None
    best_set_weight: Optional[float] = None
    best_set_reps: Optional[int] = None
    avg_rpe: Optional[float] = None

class SessionExerciseCreate(BaseModel):
    exercise_id: int
    sets_completed: int
    reps_completed: int
    weight: float
    notes: Optional[str] = None
    sets_data: Optional[str] = None  # JSON string
    time_under_tension: Optional[float] = None
    total_volume: Optional[float] = None
    best_set_weight: Optional[float] = None
    best_set_reps: Optional[int] = None
    avg_rpe: Optional[float] = None

class SessionExercise(SessionExerciseBase):
    id: int
    exercise: Exercise
    
    class Config:
        from_attributes = True

# Workout Session Schemas
class WorkoutSessionBase(BaseModel):
    workout_id: int
    notes: Optional[str] = None
    session_rpe: Optional[float] = None
    user_readiness: Optional[int] = None

class WorkoutSessionCreate(WorkoutSessionBase):
    pass

class WorkoutSessionUpdate(BaseModel):
    completed_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    session_rpe: Optional[float] = None
    user_readiness: Optional[int] = None
    training_load: Optional[float] = None
    total_volume: Optional[float] = None
    notes: Optional[str] = None
    exercises: Optional[List[SessionExerciseCreate]] = None

class WorkoutSession(WorkoutSessionBase):
    id: int
    user_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    session_rpe: Optional[float] = None
    user_readiness: Optional[int] = None
    training_load: Optional[float] = None
    total_volume: Optional[float] = None
    workout: Workout
    exercises: List[SessionExercise] = []
    
    class Config:
        from_attributes = True
