from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    workouts = relationship("Workout", back_populates="user")
    workout_sessions = relationship("WorkoutSession", back_populates="user")
    workout_plans = relationship("WorkoutPlan", back_populates="user")

class Exercise(Base):
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    muscle_group = Column(String)  # chest, back, legs, shoulders, arms, core
    equipment = Column(String)  # barbell, dumbbell, machine, bodyweight, cable
    difficulty = Column(String)  # beginner, intermediate, advanced
    instructions = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    workout_exercises = relationship("WorkoutExercise", back_populates="exercise")
    session_exercises = relationship("SessionExercise", back_populates="exercise")

class Workout(Base):
    __tablename__ = "workouts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_id = Column(Integer, ForeignKey("workout_plans.id"), nullable=True)
    name = Column(String)
    description = Column(Text)
    icon = Column(String, default="fitness")  # Icon name (e.g., "fitness", "barbell", "heart", etc.)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="workouts")
    plan = relationship("WorkoutPlan", back_populates="workouts")
    exercises = relationship("WorkoutExercise", back_populates="workout", cascade="all, delete-orphan")
    sessions = relationship("WorkoutSession", back_populates="workout")


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="workout_plans")
    workouts = relationship("Workout", back_populates="plan")

class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    sets = Column(Integer)
    reps = Column(Integer)
    rest_seconds = Column(Integer)
    order = Column(Integer)  # Order of exercise in workout
    
    workout = relationship("Workout", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="workout_exercises")

class WorkoutSession(Base):
    __tablename__ = "workout_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    workout_id = Column(Integer, ForeignKey("workouts.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Session-level metrics
    session_rpe = Column(Float, nullable=True)  # Rate of Perceived Exertion for entire session (1-10)
    user_readiness = Column(Integer, nullable=True)  # Pre-workout readiness (1-5 scale)
    training_load = Column(Float, nullable=True)  # Session RPE × duration (useful for periodization)
    total_volume = Column(Float, nullable=True)  # Sum of all volumes
    
    notes = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="workout_sessions")
    workout = relationship("Workout", back_populates="sessions")
    exercises = relationship("SessionExercise", back_populates="session", cascade="all, delete-orphan")

class SessionExercise(Base):
    __tablename__ = "session_exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("workout_sessions.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    sets_completed = Column(Integer)
    reps_completed = Column(Integer)
    weight = Column(Float)  # in kg or lbs
    
    # Per-set data stored as JSON (list of dicts)
    sets_data = Column(Text, nullable=True)  # JSON: [{weight, reps, rpe, rir, tut, rest_after}]
    
    # Exercise-level metrics
    time_under_tension = Column(Float, nullable=True)  # in seconds
    total_volume = Column(Float, nullable=True)  # weight × reps × sets
    best_set_weight = Column(Float, nullable=True)
    best_set_reps = Column(Integer, nullable=True)
    avg_rpe = Column(Float, nullable=True)  # Average Rate of Perceived Exertion
    
    notes = Column(Text, nullable=True)
    
    session = relationship("WorkoutSession", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="session_exercises")
