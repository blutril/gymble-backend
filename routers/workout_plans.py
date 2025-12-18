from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
import models
import schemas
from database import get_db

router = APIRouter()


def _validate_user(db: Session, user_id: int) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _fetch_workouts_for_plan(db: Session, user_id: int, workout_ids: List[int]) -> List[models.Workout]:
    if not workout_ids:
        return []

    workouts = db.query(models.Workout).filter(
        models.Workout.id.in_(workout_ids),
        models.Workout.user_id == user_id
    ).all()

    if len(workouts) != len(set(workout_ids)):
        raise HTTPException(status_code=404, detail="One or more workouts not found")
    return workouts


@router.post("/", response_model=schemas.WorkoutPlan, status_code=status.HTTP_201_CREATED)
def create_workout_plan(
    plan: schemas.WorkoutPlanCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    _validate_user(db, user_id)

    db_plan = models.WorkoutPlan(
        user_id=user_id,
        name=plan.name,
        description=plan.description
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)

    workouts = _fetch_workouts_for_plan(db, user_id, plan.workout_ids)
    for workout in workouts:
        workout.plan_id = db_plan.id

    db.commit()
    db.refresh(db_plan)

    return db_plan


@router.get("/", response_model=List[schemas.WorkoutPlan])
def get_workout_plans(user_id: int, db: Session = Depends(get_db)):
    _validate_user(db, user_id)

    plans = db.query(models.WorkoutPlan).options(
        joinedload(models.WorkoutPlan.workouts)
        .joinedload(models.Workout.exercises)
        .joinedload(models.WorkoutExercise.exercise)
    ).filter(models.WorkoutPlan.user_id == user_id).all()

    return plans


@router.get("/{plan_id}", response_model=schemas.WorkoutPlan)
def get_workout_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(models.WorkoutPlan).options(
        joinedload(models.WorkoutPlan.workouts)
        .joinedload(models.Workout.exercises)
        .joinedload(models.WorkoutExercise.exercise)
    ).filter(models.WorkoutPlan.id == plan_id).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")

    return plan


@router.put("/{plan_id}", response_model=schemas.WorkoutPlan)
def update_workout_plan(
    plan_id: int,
    plan_update: schemas.WorkoutPlanUpdate,
    db: Session = Depends(get_db)
):
    plan = db.query(models.WorkoutPlan).filter(models.WorkoutPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")

    if plan_update.name is not None:
        plan.name = plan_update.name

    if plan_update.description is not None:
        plan.description = plan_update.description

    if plan_update.workout_ids is not None:
        new_workouts = _fetch_workouts_for_plan(db, plan.user_id, plan_update.workout_ids)
        new_ids = {workout.id for workout in new_workouts}

        current_workouts = db.query(models.Workout).filter(models.Workout.plan_id == plan.id).all()
        for workout in current_workouts:
            if workout.id not in new_ids:
                workout.plan_id = None

        for workout in new_workouts:
            workout.plan_id = plan.id

    db.commit()
    db.refresh(plan)

    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(models.WorkoutPlan).filter(models.WorkoutPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")

    for workout in plan.workouts:
        workout.plan_id = None

    db.delete(plan)
    db.commit()

    return None
