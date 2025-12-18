"""
Script to seed the database with common exercises
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models

def seed_exercises():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check if exercises already exist
    if db.query(models.Exercise).count() > 0:
        print("Exercises already exist in the database")
        db.close()
        return
    
    exercises = [
        # Chest
        models.Exercise(
            name="Barbell Bench Press",
            description="Classic compound chest exercise",
            muscle_group="chest",
            equipment="barbell",
            difficulty="intermediate",
            instructions="Lie on bench, lower bar to chest, press up"
        ),
        models.Exercise(
            name="Dumbbell Flyes",
            description="Isolation exercise for chest",
            muscle_group="chest",
            equipment="dumbbell",
            difficulty="beginner",
            instructions="Lie on bench, arms wide, bring dumbbells together above chest"
        ),
        models.Exercise(
            name="Push-ups",
            description="Bodyweight chest exercise",
            muscle_group="chest",
            equipment="bodyweight",
            difficulty="beginner",
            instructions="Hands shoulder-width, lower chest to ground, push up"
        ),
        
        # Back
        models.Exercise(
            name="Deadlift",
            description="Compound exercise for entire back",
            muscle_group="back",
            equipment="barbell",
            difficulty="advanced",
            instructions="Grip bar, keep back straight, lift by extending hips and knees"
        ),
        models.Exercise(
            name="Pull-ups",
            description="Bodyweight back exercise",
            muscle_group="back",
            equipment="bodyweight",
            difficulty="intermediate",
            instructions="Hang from bar, pull yourself up until chin over bar"
        ),
        models.Exercise(
            name="Bent Over Rows",
            description="Compound back exercise",
            muscle_group="back",
            equipment="barbell",
            difficulty="intermediate",
            instructions="Bend at hips, pull bar to lower chest"
        ),
        
        # Legs
        models.Exercise(
            name="Barbell Squat",
            description="King of leg exercises",
            muscle_group="legs",
            equipment="barbell",
            difficulty="intermediate",
            instructions="Bar on back, squat down keeping chest up, drive through heels"
        ),
        models.Exercise(
            name="Leg Press",
            description="Machine-based leg exercise",
            muscle_group="legs",
            equipment="machine",
            difficulty="beginner",
            instructions="Feet on platform, lower weight by bending knees, press up"
        ),
        models.Exercise(
            name="Lunges",
            description="Unilateral leg exercise",
            muscle_group="legs",
            equipment="bodyweight",
            difficulty="beginner",
            instructions="Step forward, lower back knee, push back to start"
        ),
        
        # Shoulders
        models.Exercise(
            name="Overhead Press",
            description="Compound shoulder exercise",
            muscle_group="shoulders",
            equipment="barbell",
            difficulty="intermediate",
            instructions="Press bar overhead from shoulders"
        ),
        models.Exercise(
            name="Lateral Raises",
            description="Shoulder isolation exercise",
            muscle_group="shoulders",
            equipment="dumbbell",
            difficulty="beginner",
            instructions="Raise dumbbells to sides until parallel with ground"
        ),
        
        # Arms
        models.Exercise(
            name="Barbell Curl",
            description="Bicep exercise",
            muscle_group="arms",
            equipment="barbell",
            difficulty="beginner",
            instructions="Curl bar from thighs to shoulders"
        ),
        models.Exercise(
            name="Tricep Dips",
            description="Tricep bodyweight exercise",
            muscle_group="arms",
            equipment="bodyweight",
            difficulty="intermediate",
            instructions="Lower body by bending elbows, push back up"
        ),
        
        # Core
        models.Exercise(
            name="Plank",
            description="Core stability exercise",
            muscle_group="core",
            equipment="bodyweight",
            difficulty="beginner",
            instructions="Hold body straight in push-up position on forearms"
        ),
        models.Exercise(
            name="Crunches",
            description="Abdominal exercise",
            muscle_group="core",
            equipment="bodyweight",
            difficulty="beginner",
            instructions="Lie on back, curl shoulders toward hips"
        ),
    ]
    
    db.add_all(exercises)
    db.commit()
    print(f"Successfully seeded {len(exercises)} exercises")
    db.close()

if __name__ == "__main__":
    seed_exercises()
