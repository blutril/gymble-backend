from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

import models
from database import get_db
from utils.stats import WorkoutAnalytics

router = APIRouter()

templates = Jinja2Templates(directory="templates")


# Advanced Analytics Endpoints

@router.get("/user/{user_id}/comprehensive-stats")
def get_comprehensive_stats(
    user_id: int,
    days: int = 90,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive fitness dashboard with all advanced metrics
    Includes: 1RM estimates, PRs, strength/volume trends, training load, monotony, strain, readiness
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get all sessions in timeframe
    sessions = db.query(models.WorkoutSession).filter(
        models.WorkoutSession.user_id == user_id,
        models.WorkoutSession.completed_at >= cutoff_date
    ).order_by(models.WorkoutSession.completed_at.desc()).all()
    
    # Get all unique exercises trained
    exercises = db.query(models.Exercise).join(
        models.SessionExercise
    ).join(
        models.WorkoutSession
    ).filter(
        models.WorkoutSession.user_id == user_id,
        models.WorkoutSession.completed_at >= cutoff_date
    ).distinct().all()
    
    # Build comprehensive data
    stats = {
        'user_id': user_id,
        'timeframe_days': days,
        'total_sessions': len(sessions),
        'total_duration': sum(s.duration_minutes or 0 for s in sessions),
        'avg_session_duration': round(sum(s.duration_minutes or 0 for s in sessions) / len(sessions), 1) if sessions else 0,
        
        # Readiness tracking
        'readiness_scores': [s.user_readiness for s in sessions if s.user_readiness],
        'readiness_avg': round(sum(s.user_readiness for s in sessions if s.user_readiness) / len([s for s in sessions if s.user_readiness]), 1) if any(s.user_readiness for s in sessions) else 0,
        
        # Training load
        'session_rpes': [s.session_rpe for s in sessions if s.session_rpe],
        'training_loads': [s.training_load for s in sessions if s.training_load],
        'total_training_load': sum(s.training_load or 0 for s in sessions),
        
        # Volume
        'total_volume_lifted': sum(s.total_volume or 0 for s in sessions),
        'avg_volume_per_session': round(sum(s.total_volume or 0 for s in sessions) / len(sessions), 1) if sessions else 0,
        
        # Exercise-specific metrics
        'exercise_metrics': [],
        
        # Trends
        'strength_trends_by_exercise': {},
        'volume_trends_by_muscle': {},
        
        # Recovery metrics
        'weekly_stats': WorkoutAnalytics.get_weekly_stats(db, user_id, 4)
    }
    
    # Process each exercise
    for exercise in exercises:
        pr_summary = WorkoutAnalytics.get_exercise_pr_summary(db, user_id, exercise.id)
        
        # Get recent data for this exercise
        recent_sessions = [
            s for s in sessions 
            for se in s.exercises 
            if se.exercise_id == exercise.id
        ]
        
        if recent_sessions:
            exercise_metric = {
                'exercise_id': exercise.id,
                'exercise_name': exercise.name,
                'muscle_group': exercise.muscle_group,
                'times_trained': len(recent_sessions),
                'prs': pr_summary,
                'total_volume': round(sum(se.total_volume or 0 for s in sessions for se in s.exercises if se.exercise_id == exercise.id), 2)
            }
            stats['exercise_metrics'].append(exercise_metric)
        
        # Add strength trend
        trend = WorkoutAnalytics.get_strength_trend(db, user_id, exercise.id, days)
        if trend:
            stats['strength_trends_by_exercise'][exercise.name] = trend
    
    # Add volume trends by muscle group
    muscle_groups = set(e.muscle_group for e in exercises)
    for muscle in muscle_groups:
        trend = WorkoutAnalytics.get_volume_trend(db, user_id, muscle, days)
        if trend:
            stats['volume_trends_by_muscle'][muscle] = trend
    
    # Calculate monotony and strain
    training_loads = [s.training_load for s in sessions if s.training_load]
    if training_loads:
        monotony = WorkoutAnalytics.calculate_monotony(training_loads)
        strain = WorkoutAnalytics.calculate_strain(training_loads, monotony)
        stats['monotony'] = round(monotony, 2)
        stats['strain'] = round(strain, 2)
        stats['monotony_interpretation'] = (
            "Low - Good variety in training" if monotony < 1.5 
            else "Moderate - Some variation" if monotony < 2.0 
            else "High - Training is monotonous"
        )
    
    return stats


@router.get("/user/{user_id}/exercise/{exercise_id}/detailed-stats")
def get_exercise_detailed_stats(
    user_id: int,
    exercise_id: int,
    days: int = 90,
    db: Session = Depends(get_db)
):
    """Get detailed statistics for a specific exercise"""
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    exercise = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    sessions = db.query(models.WorkoutSession).filter(
        models.WorkoutSession.user_id == user_id,
        models.WorkoutSession.completed_at >= cutoff_date
    ).order_by(models.WorkoutSession.completed_at).all()
    
    exercise_data = []
    
    for session in sessions:
        for session_exercise in session.exercises:
            if session_exercise.exercise_id != exercise_id:
                continue
            
            sets_data = WorkoutAnalytics.parse_sets_data(session_exercise.sets_data)
            best_set = WorkoutAnalytics.get_best_set(sets_data)
            
            exercise_data.append({
                'date': (session.completed_at or session.started_at).isoformat(),
                'session_id': session.id,
                'sets_completed': session_exercise.sets_completed,
                'reps_completed': session_exercise.reps_completed,
                'weight': session_exercise.weight,
                'total_volume': session_exercise.total_volume,
                'time_under_tension': session_exercise.time_under_tension,
                'avg_rpe': session_exercise.avg_rpe,
                'best_set': best_set,
                'estimated_1rm': WorkoutAnalytics.calculate_one_rm_brzycki(
                    best_set['weight'], best_set['reps']
                ) if best_set else None,
                'sets_data': sets_data
            })
    
    pr_summary = WorkoutAnalytics.get_exercise_pr_summary(db, user_id, exercise_id)
    strength_trend = WorkoutAnalytics.get_strength_trend(db, user_id, exercise_id, days)
    
    return {
        'exercise_id': exercise_id,
        'exercise_name': exercise.name,
        'muscle_group': exercise.muscle_group,
        'times_trained': len(exercise_data),
        'total_volume_lifted': round(sum(e['total_volume'] or 0 for e in exercise_data), 2),
        'avg_session_volume': round(sum(e['total_volume'] or 0 for e in exercise_data) / len(exercise_data), 2) if exercise_data else 0,
        'personal_records': pr_summary,
        'strength_progression': strength_trend,
        'sessions': exercise_data
    }


@router.get("/user/{user_id}/muscle-group/{muscle_group}/summary")
def get_muscle_group_summary(
    user_id: int,
    muscle_group: str,
    days: int = 90,
    db: Session = Depends(get_db)
):
    """Get summary statistics for all exercises targeting a muscle group"""
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    exercises = db.query(models.Exercise).filter(
        models.Exercise.muscle_group == muscle_group
    ).all()
    
    if not exercises:
        raise HTTPException(status_code=404, detail="No exercises found for this muscle group")
    
    exercise_summaries = []
    total_volume = 0
    total_sessions = 0
    
    for exercise in exercises:
        sessions = db.query(models.WorkoutSession).filter(
            models.WorkoutSession.user_id == user_id,
            models.WorkoutSession.completed_at >= cutoff_date
        ).all()
        
        exercise_volume = 0
        exercise_count = 0
        
        for session in sessions:
            for session_exercise in session.exercises:
                if session_exercise.exercise_id == exercise.id:
                    if session_exercise.total_volume:
                        exercise_volume += session_exercise.total_volume
                    exercise_count += 1
        
        if exercise_count > 0:
            total_volume += exercise_volume
            total_sessions += exercise_count
            
            exercise_summaries.append({
                'exercise_id': exercise.id,
                'exercise_name': exercise.name,
                'times_trained': exercise_count,
                'total_volume': round(exercise_volume, 2),
                'avg_volume_per_session': round(exercise_volume / exercise_count, 2)
            })
    
    volume_trend = WorkoutAnalytics.get_volume_trend(db, user_id, muscle_group, days)
    
    return {
        'muscle_group': muscle_group,
        'total_volume_lifted': round(total_volume, 2),
        'total_sessions': total_sessions,
        'exercises': exercise_summaries,
        'volume_progression': volume_trend
    }


@router.get("/user/{user_id}/readiness-correlation")
def get_readiness_correlation(
    user_id: int,
    days: int = 90,
    db: Session = Depends(get_db)
):
    """
    Analyze correlation between pre-workout readiness and session performance
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    sessions = db.query(models.WorkoutSession).filter(
        models.WorkoutSession.user_id == user_id,
        models.WorkoutSession.completed_at >= cutoff_date,
        models.WorkoutSession.user_readiness.isnot(None),
        models.WorkoutSession.training_load.isnot(None)
    ).all()
    
    if not sessions:
        return {
            'user_id': user_id,
            'message': 'Not enough data (need readiness scores and training load)',
            'sessions_analyzed': 0
        }
    
    # Group by readiness level
    readiness_groups = {}
    for session in sessions:
        readiness = session.user_readiness
        if readiness not in readiness_groups:
            readiness_groups[readiness] = []
        readiness_groups[readiness].append(session)
    
    readiness_analysis = {}
    for readiness_level in sorted(readiness_groups.keys()):
        group_sessions = readiness_groups[readiness_level]
        loads = [s.training_load for s in group_sessions if s.training_load]
        volumes = [s.total_volume for s in group_sessions if s.total_volume]
        durations = [s.duration_minutes for s in group_sessions if s.duration_minutes]
        
        readiness_analysis[f"Readiness {readiness_level}"] = {
            'session_count': len(group_sessions),
            'avg_training_load': round(sum(loads) / len(loads), 2) if loads else 0,
            'avg_volume': round(sum(volumes) / len(volumes), 2) if volumes else 0,
            'avg_duration': round(sum(durations) / len(durations), 1) if durations else 0
        }
    
    return {
        'user_id': user_id,
        'days': days,
        'sessions_analyzed': len(sessions),
        'analysis': readiness_analysis
    }


# Original HTML Dashboard Endpoints

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
