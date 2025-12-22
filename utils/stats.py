"""
Advanced workout analytics and metrics calculations
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json
from sqlalchemy.orm import Session
import models


class WorkoutAnalytics:
    """Calculate advanced workout metrics and statistics"""
    
    @staticmethod
    def calculate_one_rm_epley(weight: float, reps: int) -> float:
        """
        Calculate estimated 1-rep max using Epley formula
        1RM = weight × (1 + reps/30)
        """
        if reps <= 0:
            return weight
        return weight * (1 + reps / 30)
    
    @staticmethod
    def calculate_one_rm_brzycki(weight: float, reps: int) -> float:
        """
        Calculate estimated 1-rep max using Brzycki formula
        1RM = weight × 36 / (37 - reps)
        More accurate for higher reps (5-10 range)
        """
        if reps >= 37 or reps <= 0:
            return weight
        return weight * 36 / (37 - reps)
    
    @staticmethod
    def calculate_total_volume(weight: float, reps: int, sets: int) -> float:
        """Calculate total volume lifted: weight × reps × sets"""
        return weight * reps * sets
    
    @staticmethod
    def parse_sets_data(sets_data_json: Optional[str]) -> List[Dict]:
        """Parse JSON string of per-set data"""
        if not sets_data_json:
            return []
        try:
            return json.loads(sets_data_json)
        except:
            return []
    
    @staticmethod
    def get_best_set(sets_data: List[Dict]) -> Optional[Dict]:
        """Find best set by weight × reps product"""
        if not sets_data:
            return None
        best = max(sets_data, key=lambda s: s.get('weight', 0) * s.get('reps', 0))
        return best
    
    @staticmethod
    def calculate_avg_rpe(sets_data: List[Dict]) -> Optional[float]:
        """Calculate average RPE across sets"""
        rpe_values = [s.get('rpe') for s in sets_data if s.get('rpe') is not None]
        if not rpe_values:
            return None
        return sum(rpe_values) / len(rpe_values)
    
    @staticmethod
    def get_personal_records(
        db: Session, 
        user_id: int, 
        exercise_id: int,
        metric: str = "weight"  # "weight", "reps", "volume", "1rm"
    ) -> Optional[Dict]:
        """
        Get personal record for an exercise
        metric options: "weight", "reps", "volume", "1rm"
        """
        sessions = db.query(models.WorkoutSession).filter(
            models.WorkoutSession.user_id == user_id
        ).all()
        
        records = []
        
        for session in sessions:
            for exercise in session.exercises:
                if exercise.exercise_id != exercise_id:
                    continue
                
                sets_data = WorkoutAnalytics.parse_sets_data(exercise.sets_data)
                
                if metric == "weight":
                    max_weight = max([s.get('weight', 0) for s in sets_data], default=0)
                    if max_weight > 0:
                        records.append({
                            'value': max_weight,
                            'session_id': session.id,
                            'date': session.completed_at or session.started_at,
                            'reps': next((s.get('reps') for s in sets_data 
                                         if s.get('weight') == max_weight), 0)
                        })
                
                elif metric == "reps":
                    max_reps = max([s.get('reps', 0) for s in sets_data], default=0)
                    if max_reps > 0:
                        records.append({
                            'value': max_reps,
                            'session_id': session.id,
                            'date': session.completed_at or session.started_at,
                            'weight': next((s.get('weight') for s in sets_data 
                                           if s.get('reps') == max_reps), 0)
                        })
                
                elif metric == "volume":
                    if exercise.total_volume:
                        records.append({
                            'value': exercise.total_volume,
                            'session_id': session.id,
                            'date': session.completed_at or session.started_at
                        })
                
                elif metric == "1rm":
                    best_set = WorkoutAnalytics.get_best_set(sets_data)
                    if best_set:
                        one_rm = WorkoutAnalytics.calculate_one_rm_brzycki(
                            best_set.get('weight', 0),
                            best_set.get('reps', 1)
                        )
                        records.append({
                            'value': one_rm,
                            'session_id': session.id,
                            'date': session.completed_at or session.started_at
                        })
        
        if not records:
            return None
        
        best_record = max(records, key=lambda r: r['value'])
        return best_record
    
    @staticmethod
    def get_strength_trend(
        db: Session,
        user_id: int,
        exercise_id: int,
        days: int = 90
    ) -> List[Dict]:
        """
        Get strength progression over time (weight × reps estimate)
        Returns list of {date, weight, reps, estimated_1rm}
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        sessions = db.query(models.WorkoutSession).filter(
            models.WorkoutSession.user_id == user_id,
            models.WorkoutSession.completed_at >= cutoff_date
        ).order_by(models.WorkoutSession.completed_at).all()
        
        trend = []
        for session in sessions:
            for exercise in session.exercises:
                if exercise.exercise_id != exercise_id:
                    continue
                
                sets_data = WorkoutAnalytics.parse_sets_data(exercise.sets_data)
                best_set = WorkoutAnalytics.get_best_set(sets_data)
                
                if best_set:
                    one_rm = WorkoutAnalytics.calculate_one_rm_brzycki(
                        best_set.get('weight', 0),
                        best_set.get('reps', 1)
                    )
                    trend.append({
                        'date': (session.completed_at or session.started_at).isoformat(),
                        'weight': best_set.get('weight'),
                        'reps': best_set.get('reps'),
                        'estimated_1rm': round(one_rm, 2)
                    })
        
        return trend
    
    @staticmethod
    def get_volume_trend(
        db: Session,
        user_id: int,
        muscle_group: Optional[str] = None,
        days: int = 90
    ) -> List[Dict]:
        """
        Get volume progression over time per muscle group or overall
        Returns list of {date, total_volume, exercise_count}
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        sessions = db.query(models.WorkoutSession).filter(
            models.WorkoutSession.user_id == user_id,
            models.WorkoutSession.completed_at >= cutoff_date
        ).order_by(models.WorkoutSession.completed_at).all()
        
        trend = []
        for session in sessions:
            session_volume = 0
            exercise_count = 0
            
            for exercise in session.exercises:
                if muscle_group and exercise.exercise.muscle_group != muscle_group:
                    continue
                
                if exercise.total_volume:
                    session_volume += exercise.total_volume
                    exercise_count += 1
            
            if exercise_count > 0:
                trend.append({
                    'date': (session.completed_at or session.started_at).isoformat(),
                    'total_volume': round(session_volume, 2),
                    'exercise_count': exercise_count,
                    'avg_volume_per_exercise': round(session_volume / exercise_count, 2)
                })
        
        return trend
    
    @staticmethod
    def calculate_monotony(training_loads: List[float]) -> float:
        """
        Calculate monotony as coefficient of variation of daily training loads
        Low monotony = varied training loads (good - prevents adaptation plateau)
        High monotony = consistent training loads (monotonous - may lead to plateau)
        
        Monotony = mean(loads) / std(loads)
        """
        if len(training_loads) < 2:
            return 0
        
        mean_load = sum(training_loads) / len(training_loads)
        variance = sum((x - mean_load) ** 2 for x in training_loads) / len(training_loads)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return 1.0
        
        return mean_load / std_dev
    
    @staticmethod
    def calculate_strain(training_loads: List[float], monotony: float) -> float:
        """
        Calculate strain (acute fatigue index)
        Strain = weekly_load × monotony
        
        Used to assess training stress: high strain = high fatigue risk
        """
        weekly_load = sum(training_loads)
        return weekly_load * monotony
    
    @staticmethod
    def get_weekly_stats(db: Session, user_id: int, weeks: int = 1) -> List[Dict]:
        """
        Get weekly training load statistics
        Returns list of {week_start, weekly_load, monotony, strain, readiness_avg}
        """
        now = datetime.utcnow()
        stats = []
        
        for week_offset in range(weeks):
            week_start = now - timedelta(weeks=week_offset, days=now.weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            week_end = week_start + timedelta(days=7)
            
            sessions = db.query(models.WorkoutSession).filter(
                models.WorkoutSession.user_id == user_id,
                models.WorkoutSession.started_at >= week_start,
                models.WorkoutSession.started_at < week_end,
                models.WorkoutSession.completed_at.isnot(None)
            ).all()
            
            if not sessions:
                continue
            
            training_loads = []
            readiness_scores = []
            
            for session in sessions:
                # Calculate session training load (RPE × duration)
                if session.session_rpe and session.duration_minutes:
                    load = (session.session_rpe / 10) * session.duration_minutes
                    training_loads.append(load)
                
                if session.user_readiness:
                    readiness_scores.append(session.user_readiness)
            
            if training_loads:
                weekly_load = sum(training_loads)
                monotony = WorkoutAnalytics.calculate_monotony(training_loads)
                strain = WorkoutAnalytics.calculate_strain(training_loads, monotony)
                avg_readiness = sum(readiness_scores) / len(readiness_scores) if readiness_scores else 0
                
                stats.append({
                    'week_start': week_start.isoformat(),
                    'session_count': len(sessions),
                    'weekly_load': round(weekly_load, 2),
                    'monotony': round(monotony, 2),
                    'strain': round(strain, 2),
                    'readiness_avg': round(avg_readiness, 1) if readiness_scores else 0
                })
        
        return stats
    
    @staticmethod
    def get_exercise_pr_summary(
        db: Session,
        user_id: int,
        exercise_id: int
    ) -> Dict:
        """
        Get comprehensive PR summary for an exercise
        """
        return {
            'weight_pr': WorkoutAnalytics.get_personal_records(db, user_id, exercise_id, "weight"),
            'reps_pr': WorkoutAnalytics.get_personal_records(db, user_id, exercise_id, "reps"),
            'volume_pr': WorkoutAnalytics.get_personal_records(db, user_id, exercise_id, "volume"),
            'estimated_1rm_pr': WorkoutAnalytics.get_personal_records(db, user_id, exercise_id, "1rm"),
        }
    
    @staticmethod
    def is_new_pr(
        db: Session,
        user_id: int,
        exercise_id: int,
        weight: float,
        reps: int,
        exclude_session_id: Optional[int] = None
    ) -> Dict[str, bool]:
        """
        Check if a set is a new personal record
        Returns dict with keys: 'weight_pr', 'reps_pr', 'volume_pr', '1rm_pr'
        """
        is_pr = {
            'weight_pr': False,
            'reps_pr': False,
            'volume_pr': False,
            '1rm_pr': False
        }
        
        if weight <= 0 or reps <= 0:
            return is_pr
        
        # Get previous sessions (excluding current session if provided)
        sessions = db.query(models.WorkoutSession).filter(
            models.WorkoutSession.user_id == user_id
        ).all()
        
        prev_weight_pr = 0
        prev_reps_pr = 0
        prev_volume_pr = 0
        prev_1rm_pr = 0
        
        for session in sessions:
            if exclude_session_id and session.id == exclude_session_id:
                continue
            if not session.completed_at:
                continue
                
            for exercise in session.exercises:
                if exercise.exercise_id != exercise_id:
                    continue
                
                sets_data = WorkoutAnalytics.parse_sets_data(exercise.sets_data)
                
                # Check weight PR
                max_weight = max([s.get('weight', 0) for s in sets_data], default=0)
                if max_weight > prev_weight_pr:
                    prev_weight_pr = max_weight
                
                # Check reps PR (at same weight or more)
                for s in sets_data:
                    if s.get('weight', 0) >= weight and s.get('reps', 0) > prev_reps_pr:
                        prev_reps_pr = s.get('reps', 0)
                
                # Check volume PR
                if exercise.total_volume and exercise.total_volume > prev_volume_pr:
                    prev_volume_pr = exercise.total_volume
                
                # Check 1RM PR
                best_set = WorkoutAnalytics.get_best_set(sets_data)
                if best_set:
                    one_rm = WorkoutAnalytics.calculate_one_rm_brzycki(
                        best_set.get('weight', 0),
                        best_set.get('reps', 1)
                    )
                    if one_rm > prev_1rm_pr:
                        prev_1rm_pr = one_rm
        
        # Check if current set is a PR
        current_1rm = WorkoutAnalytics.calculate_one_rm_brzycki(weight, reps)
        current_volume = weight * reps
        
        is_pr['weight_pr'] = weight > prev_weight_pr
        is_pr['reps_pr'] = reps > prev_reps_pr
        is_pr['volume_pr'] = current_volume > prev_volume_pr
        is_pr['1rm_pr'] = current_1rm > prev_1rm_pr
        
        return is_pr
