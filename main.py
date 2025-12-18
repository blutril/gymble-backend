from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import workouts, exercises, users, sessions, dashboard, workout_plans
from database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gymble API",
    description="A gym workout tracking API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(workouts.router, prefix="/api/workouts", tags=["workouts"])
app.include_router(workout_plans.router, prefix="/api/workout-plans", tags=["workout plans"])
app.include_router(exercises.router, prefix="/api/exercises", tags=["exercises"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(dashboard.router, tags=["dashboard"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Gymble API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
