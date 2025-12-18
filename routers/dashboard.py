from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

import models
from database import get_db

router = APIRouter()

templates = Jinja2Templates(directory="templates")


def _format_datetime(value: Optional[datetime]) -> str:
    if not value:
        return "—"
    return value.strftime("%b %d, %Y %H:%M")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    total_users = db.query(models.User).count()
    total_workouts = db.query(models.Workout).count()
    total_exercises = db.query(models.Exercise).count()
    total_sessions = db.query(models.WorkoutSession).count()

    completed_sessions = (
        db.query(models.WorkoutSession)
        .filter(models.WorkoutSession.completed_at.is_not(None))
        .count()
    )
    active_sessions = total_sessions - completed_sessions

    avg_duration = (
        db.query(func.avg(models.WorkoutSession.duration_minutes))
        .filter(models.WorkoutSession.duration_minutes.is_not(None))
        .scalar()
    )
    avg_duration_display = f"{avg_duration:.0f} min" if avg_duration else "—"

    recent_workouts: List[models.Workout] = (
        db.query(models.Workout)
        .options(
            selectinload(models.Workout.user),
            selectinload(models.Workout.exercises),
        )
        .order_by(models.Workout.updated_at.desc())
        .limit(5)
        .all()
    )

    recent_sessions: List[models.WorkoutSession] = (
        db.query(models.WorkoutSession)
        .options(
            selectinload(models.WorkoutSession.workout),
            selectinload(models.WorkoutSession.user),
        )
        .order_by(models.WorkoutSession.started_at.desc())
        .limit(5)
        .all()
    )

    days_back = 6
    window_start = datetime.utcnow() - timedelta(days=days_back)
    sessions_by_day = (
        db.query(
            func.date(models.WorkoutSession.started_at).label("day"),
            func.count(models.WorkoutSession.id).label("count"),
        )
        .filter(models.WorkoutSession.started_at >= window_start)
        .group_by(func.date(models.WorkoutSession.started_at))
        .order_by(func.date(models.WorkoutSession.started_at))
        .all()
    )

    workouts_per_user = (
        db.query(
            models.User.username.label("username"),
            func.count(models.Workout.id).label("count"),
        )
        .join(models.Workout, models.Workout.user_id == models.User.id)
        .group_by(models.User.id)
        .order_by(func.count(models.Workout.id).desc())
        .limit(5)
        .all()
    )

    top_exercises = (
        db.query(
            models.Exercise.name.label("name"),
            func.count(models.WorkoutExercise.id).label("usage_count"),
        )
        .join(models.WorkoutExercise, models.Exercise.id == models.WorkoutExercise.exercise_id)
        .group_by(models.Exercise.id)
        .order_by(func.count(models.WorkoutExercise.id).desc())
        .limit(5)
        .all()
    )

    muscle_distribution = (
        db.query(
            models.Exercise.muscle_group.label("group"),
            func.count(models.Exercise.id).label("total"),
        )
        .group_by(models.Exercise.muscle_group)
        .order_by(func.count(models.Exercise.id).desc())
        .all()
    )

    context: Dict[str, object] = {
        "request": request,
        "totals": {
            "users": total_users,
            "workouts": total_workouts,
            "exercises": total_exercises,
            "sessions": total_sessions,
        },
        "session_stats": {
            "completed": completed_sessions,
            "active": active_sessions,
            "average_duration": avg_duration_display,
        },
        "recent_workouts": [
            {
                "id": workout.id,
                "name": workout.name,
                "owner": (workout.user.full_name or workout.user.username) if workout.user else "—",
                "exercise_count": len(workout.exercises or []),
                "updated_at": _format_datetime(workout.updated_at or workout.created_at),
            }
            for workout in recent_workouts
        ],
        "recent_sessions": [
            {
                "id": session.id,
                "workout": session.workout.name if session.workout else "—",
                "user": session.user.full_name or session.user.username if session.user else "—",
                "started_at": _format_datetime(session.started_at),
                "status": "Completed" if session.completed_at else "In Progress",
                "duration": f"{session.duration_minutes} min" if session.duration_minutes else "—",
            }
            for session in recent_sessions
        ],
        "top_exercises": [
            {"name": row.name, "usage_count": row.usage_count}
            for row in top_exercises
        ],
        "muscle_distribution": [
            {"group": row.group or "unspecified", "total": row.total}
            for row in muscle_distribution
        ],
    }
    context["generated_at"] = _format_datetime(datetime.utcnow())

    date_range = [
        (window_start + timedelta(days=offset)).date()
        for offset in range(days_back + 1)
    ]

    counts_map: Dict[str, int] = {
        day.isoformat(): 0 for day in date_range
    }

    for row in sessions_by_day:
        day_value = row.day
        if isinstance(day_value, datetime):
            key = day_value.date().isoformat()
        else:
            key = str(day_value)
        if key in counts_map:
            counts_map[key] = row.count

    sessions_chart = {
        "labels": [day.strftime("%b %d") for day in date_range],
        "counts": [counts_map[day.isoformat()] for day in date_range],
    }

    workouts_chart = {
        "labels": [row.username for row in workouts_per_user],
        "counts": [row.count for row in workouts_per_user],
    }

    muscle_chart = {
        "labels": [entry["group"].title() for entry in context["muscle_distribution"]],
        "counts": [entry["total"] for entry in context["muscle_distribution"]],
    }

    context["charts"] = {
        "sessions_by_day": sessions_chart,
        "workouts_per_user": workouts_chart,
        "muscle_distribution": muscle_chart,
    }

    return templates.TemplateResponse("dashboard.html", context)
