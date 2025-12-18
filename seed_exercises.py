"""
Script to seed the database with an expanded catalog of common exercises.
"""
from database import SessionLocal, engine, Base
import models


def seed_exercises():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    exercise_data = [
        # Chest
        {
            "name": "Barbell Bench Press",
            "description": "Classic compound chest exercise",
            "muscle_group": "chest",
            "equipment": "barbell",
            "difficulty": "intermediate",
            "instructions": "Lie on bench, lower bar to chest, press up",
        },
        {
            "name": "Incline Dumbbell Press",
            "description": "Targets upper chest with free weights",
            "muscle_group": "chest",
            "equipment": "dumbbell",
            "difficulty": "intermediate",
            "instructions": "On incline bench press dumbbells upward at 45 degrees",
        },
        {
            "name": "Dumbbell Flyes",
            "description": "Isolation exercise for chest",
            "muscle_group": "chest",
            "equipment": "dumbbell",
            "difficulty": "beginner",
            "instructions": "Lie on bench, arms wide, bring dumbbells together above chest",
        },
        {
            "name": "Push-ups",
            "description": "Bodyweight chest exercise",
            "muscle_group": "chest",
            "equipment": "bodyweight",
            "difficulty": "beginner",
            "instructions": "Hands shoulder-width, lower chest to ground, push up",
        },
        {
            "name": "Cable Crossover",
            "description": "Chest isolation using cables",
            "muscle_group": "chest",
            "equipment": "cable",
            "difficulty": "intermediate",
            "instructions": "Pull handles together in front keeping slight elbow bend",
        },
        {
            "name": "Chest Dip",
            "description": "Bodyweight dip emphasizing chest",
            "muscle_group": "chest",
            "equipment": "bodyweight",
            "difficulty": "advanced",
            "instructions": "Lean forward on dip bars, lower until elbows 90 degrees, press up",
        },

        # Back
        {
            "name": "Deadlift",
            "description": "Compound exercise for entire posterior chain",
            "muscle_group": "back",
            "equipment": "barbell",
            "difficulty": "advanced",
            "instructions": "Grip bar, keep back straight, lift by extending hips and knees",
        },
        {
            "name": "Pull-ups",
            "description": "Bodyweight back exercise",
            "muscle_group": "back",
            "equipment": "bodyweight",
            "difficulty": "intermediate",
            "instructions": "Hang from bar, pull yourself up until chin over bar",
        },
        {
            "name": "Bent Over Row",
            "description": "Compound back exercise",
            "muscle_group": "back",
            "equipment": "barbell",
            "difficulty": "intermediate",
            "instructions": "Bend at hips, pull bar to lower chest",
        },
        {
            "name": "Lat Pulldown",
            "description": "Machine-based vertical pull",
            "muscle_group": "back",
            "equipment": "machine",
            "difficulty": "beginner",
            "instructions": "Pull bar to collarbone while keeping torso upright",
        },
        {
            "name": "Seated Cable Row",
            "description": "Horizontal pull for mid-back",
            "muscle_group": "back",
            "equipment": "cable",
            "difficulty": "beginner",
            "instructions": "Row handle to torso with neutral spine",
        },
        {
            "name": "Single-Arm Dumbbell Row",
            "description": "Unilateral back exercise",
            "muscle_group": "back",
            "equipment": "dumbbell",
            "difficulty": "beginner",
            "instructions": "Support body on bench, pull dumbbell toward hip",
        },
        {
            "name": "Face Pull",
            "description": "Upper-back and rear delt exercise",
            "muscle_group": "back",
            "equipment": "cable",
            "difficulty": "intermediate",
            "instructions": "Pull rope attachment to forehead keeping elbows high",
        },

        # Legs
        {
            "name": "Barbell Back Squat",
            "description": "Foundational compound leg movement",
            "muscle_group": "legs",
            "equipment": "barbell",
            "difficulty": "intermediate",
            "instructions": "Bar on back, squat down keeping chest up, drive through heels",
        },
        {
            "name": "Front Squat",
            "description": "Quad-focused squat variation",
            "muscle_group": "legs",
            "equipment": "barbell",
            "difficulty": "advanced",
            "instructions": "Rest bar on front delts, maintain upright torso through squat",
        },
        {
            "name": "Romanian Deadlift",
            "description": "Hip hinge targeting hamstrings",
            "muscle_group": "legs",
            "equipment": "barbell",
            "difficulty": "intermediate",
            "instructions": "Lower bar by hinging at hips with soft knees, squeeze glutes to stand",
        },
        {
            "name": "Walking Lunge",
            "description": "Unilateral leg exercise emphasizing balance",
            "muscle_group": "legs",
            "equipment": "bodyweight",
            "difficulty": "beginner",
            "instructions": "Step forward, lower back knee toward floor, push through front heel",
        },
        {
            "name": "Leg Press",
            "description": "Machine-based leg exercise",
            "muscle_group": "legs",
            "equipment": "machine",
            "difficulty": "beginner",
            "instructions": "Feet on platform, lower weight by bending knees, press up",
        },
        {
            "name": "Leg Extension",
            "description": "Isolation movement for quadriceps",
            "muscle_group": "legs",
            "equipment": "machine",
            "difficulty": "beginner",
            "instructions": "Extend knees to lift pad, control descent",
        },
        {
            "name": "Seated Leg Curl",
            "description": "Hamstring isolation on machine",
            "muscle_group": "legs",
            "equipment": "machine",
            "difficulty": "beginner",
            "instructions": "Curl pad toward glutes keeping hips pressed into seat",
        },
        {
            "name": "Standing Calf Raise",
            "description": "Calf strengthening exercise",
            "muscle_group": "legs",
            "equipment": "machine",
            "difficulty": "beginner",
            "instructions": "Rise onto toes with controlled tempo, lower heels fully",
        },

        # Glutes
        {
            "name": "Barbell Hip Thrust",
            "description": "Powerful glute bridge variation",
            "muscle_group": "glutes",
            "equipment": "barbell",
            "difficulty": "intermediate",
            "instructions": "Upper back on bench, drive hips up until knees at 90 degrees",
        },
        {
            "name": "Glute Bridge",
            "description": "Bodyweight bridge for glute activation",
            "muscle_group": "glutes",
            "equipment": "bodyweight",
            "difficulty": "beginner",
            "instructions": "Lie on back, press hips upward by squeezing glutes",
        },

        # Shoulders
        {
            "name": "Overhead Press",
            "description": "Compound shoulder exercise",
            "muscle_group": "shoulders",
            "equipment": "barbell",
            "difficulty": "intermediate",
            "instructions": "Press bar overhead from shoulders",
        },
        {
            "name": "Arnold Press",
            "description": "Rotational dumbbell press",
            "muscle_group": "shoulders",
            "equipment": "dumbbell",
            "difficulty": "intermediate",
            "instructions": "Rotate palms during press from chest to overhead",
        },
        {
            "name": "Lateral Raise",
            "description": "Medial delt isolation",
            "muscle_group": "shoulders",
            "equipment": "dumbbell",
            "difficulty": "beginner",
            "instructions": "Raise dumbbells to sides until parallel with ground",
        },
        {
            "name": "Rear Delt Fly",
            "description": "Posterior shoulder exercise",
            "muscle_group": "shoulders",
            "equipment": "machine",
            "difficulty": "beginner",
            "instructions": "On pec deck set handles back, open arms squeezing shoulder blades",
        },
        {
            "name": "Upright Row",
            "description": "Upper trap and shoulder movement",
            "muscle_group": "shoulders",
            "equipment": "barbell",
            "difficulty": "intermediate",
            "instructions": "Pull bar vertically toward chin keeping elbows higher than wrists",
        },

        # Arms
        {
            "name": "Barbell Curl",
            "description": "Bicep exercise",
            "muscle_group": "arms",
            "equipment": "barbell",
            "difficulty": "beginner",
            "instructions": "Curl bar from thighs to shoulders",
        },
        {
            "name": "Hammer Curl",
            "description": "Neutral-grip curl targeting brachialis",
            "muscle_group": "arms",
            "equipment": "dumbbell",
            "difficulty": "beginner",
            "instructions": "Curl dumbbells with palms facing each other",
        },
        {
            "name": "Concentration Curl",
            "description": "Seated single-arm curl",
            "muscle_group": "arms",
            "equipment": "dumbbell",
            "difficulty": "beginner",
            "instructions": "Elbow inside thigh, curl dumbbell toward shoulder",
        },
        {
            "name": "Skull Crusher",
            "description": "Lying tricep extension",
            "muscle_group": "arms",
            "equipment": "barbell",
            "difficulty": "intermediate",
            "instructions": "Lower bar toward forehead, extend elbows to lockout",
        },
        {
            "name": "Tricep Pushdown",
            "description": "Cable tricep isolation",
            "muscle_group": "arms",
            "equipment": "cable",
            "difficulty": "beginner",
            "instructions": "Press handle downward while keeping upper arms fixed",
        },
        {
            "name": "Close-Grip Bench Press",
            "description": "Tricep focused bench press",
            "muscle_group": "arms",
            "equipment": "barbell",
            "difficulty": "intermediate",
            "instructions": "Grip bar shoulder-width, lower to chest, press driven by triceps",
        },
        {
            "name": "Tricep Dip",
            "description": "Parallel bar dip targeting triceps",
            "muscle_group": "arms",
            "equipment": "bodyweight",
            "difficulty": "intermediate",
            "instructions": "Lower body by bending elbows, push back up",
        },

        # Core
        {
            "name": "Plank",
            "description": "Core stability exercise",
            "muscle_group": "core",
            "equipment": "bodyweight",
            "difficulty": "beginner",
            "instructions": "Hold body straight in push-up position on forearms",
        },
        {
            "name": "Crunch",
            "description": "Abdominal flexion",
            "muscle_group": "core",
            "equipment": "bodyweight",
            "difficulty": "beginner",
            "instructions": "Lie on back, curl shoulders toward hips",
        },
        {
            "name": "Hanging Leg Raise",
            "description": "Lower abdominal exercise",
            "muscle_group": "core",
            "equipment": "bodyweight",
            "difficulty": "intermediate",
            "instructions": "Hang from bar, raise legs to hip height or higher",
        },
        {
            "name": "Russian Twist",
            "description": "Rotational core movement",
            "muscle_group": "core",
            "equipment": "bodyweight",
            "difficulty": "beginner",
            "instructions": "Sit with feet elevated, rotate torso side to side",
        },
        {
            "name": "Bicycle Crunch",
            "description": "Dynamic ab exercise",
            "muscle_group": "core",
            "equipment": "bodyweight",
            "difficulty": "beginner",
            "instructions": "Alternate elbow to opposite knee in cycling motion",
        },
        {
            "name": "Mountain Climber",
            "description": "Core and cardio combo",
            "muscle_group": "core",
            "equipment": "bodyweight",
            "difficulty": "intermediate",
            "instructions": "In plank drive knees toward chest alternating quickly",
        },

        # Conditioning
        {
            "name": "Burpee",
            "description": "Full-body conditioning drill",
            "muscle_group": "full body",
            "equipment": "bodyweight",
            "difficulty": "intermediate",
            "instructions": "Squat, kick feet back, perform push-up, jump explosively",
        },
        {
            "name": "Kettlebell Swing",
            "description": "Explosive hip hinge cardio move",
            "muscle_group": "full body",
            "equipment": "kettlebell",
            "difficulty": "intermediate",
            "instructions": "Hinge at hips, swing kettlebell to shoulder height with hip drive",
        },
        {
            "name": "Farmer's Carry",
            "description": "Loaded carry for grip and core",
            "muscle_group": "full body",
            "equipment": "dumbbell",
            "difficulty": "beginner",
            "instructions": "Walk with heavy weights at sides maintaining upright posture",
        },
    ]

    existing_names = {name for (name,) in db.query(models.Exercise.name).all()}
    new_entries = []

    for entry in exercise_data:
        if entry["name"] in existing_names:
            continue
        new_entries.append(models.Exercise(**entry))

    if not new_entries:
        print("All seed exercises already exist in the database")
        db.close()
        return

    db.add_all(new_entries)
    db.commit()
    print(f"Added {len(new_entries)} exercises. Total catalog size: {len(existing_names) + len(new_entries)}")
    db.close()


if __name__ == "__main__":
    seed_exercises()
