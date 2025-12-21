from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import WorkoutPlan, Workout, Base
import time

# Wait for database to be ready
max_retries = 5
retry_count = 0
while retry_count < max_retries:
    try:
        # Test connection
        with engine.connect() as conn:
            pass
        break
    except Exception as e:
        retry_count += 1
        print(f"Waiting for database... ({retry_count}/{max_retries})")
        time.sleep(2)

if retry_count >= max_retries:
    print("Could not connect to database")
    exit(1)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Get workouts for user 2
    workouts = db.query(Workout).filter(Workout.user_id == 2).all()
    print(f"Found {len(workouts)} workouts for user 2")
    
    # Check if plans already exist
    existing_plans = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == 2).all()
    print(f"Found {len(existing_plans)} existing plans for user 2")
    
    if len(existing_plans) == 0 and len(workouts) > 0:
        # Create a workout plan with all workouts
        plan = WorkoutPlan(
            user_id=2,
            name="Full Week Training",
            description="A complete workout plan with all your exercises"
        )
        db.add(plan)
        db.flush()
        
        # Associate workouts with the plan
        for workout in workouts:
            workout.plan_id = plan.id
        
        db.commit()
        print(f"Created workout plan 'Full Week Training' with {len(workouts)} workouts")
        
        # Create a second plan if there are at least 2 workouts
        if len(workouts) >= 2:
            plan2 = WorkoutPlan(
                user_id=2,
                name="Upper Body Focus",
                description="Focused on upper body training"
            )
            db.add(plan2)
            db.flush()
            
            # Add first 2 workouts to this plan
            for workout in workouts[:2]:
                workout.plan_id = plan2.id
            
            db.commit()
            print(f"Created workout plan 'Upper Body Focus' with 2 workouts")
    else:
        print("Plans already exist or no workouts found")

finally:
    db.close()
