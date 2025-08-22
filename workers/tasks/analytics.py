"""Analytics processing tasks for the worker system."""

import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

from celery import current_task
import structlog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from workers.celery_app import celery_app
from workers.config import settings

logger = structlog.get_logger()


@celery_app.task(bind=True, name="workers.tasks.analytics.process_user_analytics")
def process_user_analytics_task(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process analytics for a specific user."""
    start_time = time.time()
    
    try:
        user_id = user_data.get("user_id")
        date_range = user_data.get("date_range", "7d")  # 7d, 30d, 90d
        
        logger.info(
            "Starting user analytics task",
            task_id=self.request.id,
            user_id=user_id,
            date_range=date_range
        )
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Processing user analytics", "progress": 10}
        )
        
        # Calculate date range
        end_date = datetime.now()
        if date_range == "7d":
            start_date = end_date - timedelta(days=7)
        elif date_range == "30d":
            start_date = end_date - timedelta(days=30)
        elif date_range == "90d":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=7)
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Fetching user data", "progress": 30}
        )
        
        # In a real implementation, you would fetch data from the database
        # For now, we'll simulate the data
        mock_data = _generate_mock_user_data(user_id, start_date, end_date)
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Analyzing data", "progress": 60}
        )
        
        # Process analytics
        analytics_result = _process_user_analytics(mock_data)
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Generating visualizations", "progress": 80}
        )
        
        # Generate visualizations
        charts = _generate_user_charts(mock_data, user_id)
        
        processing_time = time.time() - start_time
        
        result = {
            "user_id": user_id,
            "task_id": self.request.id,
            "date_range": date_range,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "analytics": analytics_result,
            "charts": charts,
            "processing_time": processing_time,
            "status": "completed",
            "timestamp": time.time()
        }
        
        logger.info(
            "User analytics completed",
            task_id=self.request.id,
            user_id=user_id,
            processing_time=processing_time
        )
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "User analytics task failed",
            task_id=self.request.id,
            user_id=user_data.get("user_id"),
            error=str(e),
            processing_time=processing_time
        )
        raise


@celery_app.task(bind=True, name="workers.tasks.analytics.process_platform_analytics")
def process_platform_analytics_task(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process platform-wide analytics."""
    start_time = time.time()
    
    try:
        date_range = analytics_data.get("date_range", "7d")
        metrics = analytics_data.get("metrics", ["users", "sessions", "scoring"])
        
        logger.info(
            "Starting platform analytics task",
            task_id=self.request.id,
            date_range=date_range,
            metrics=metrics
        )
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Processing platform analytics", "progress": 10}
        )
        
        # Calculate date range
        end_date = datetime.now()
        if date_range == "7d":
            start_date = end_date - timedelta(days=7)
        elif date_range == "30d":
            start_date = end_date - timedelta(days=30)
        elif date_range == "90d":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=7)
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Fetching platform data", "progress": 30}
        )
        
        # In a real implementation, you would fetch data from the database
        # For now, we'll simulate the data
        mock_data = _generate_mock_platform_data(start_date, end_date)
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Analyzing platform data", "progress": 60}
        )
        
        # Process analytics
        analytics_result = _process_platform_analytics(mock_data, metrics)
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Generating platform charts", "progress": 80}
        )
        
        # Generate visualizations
        charts = _generate_platform_charts(mock_data, metrics)
        
        processing_time = time.time() - start_time
        
        result = {
            "task_id": self.request.id,
            "date_range": date_range,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "metrics": metrics,
            "analytics": analytics_result,
            "charts": charts,
            "processing_time": processing_time,
            "status": "completed",
            "timestamp": time.time()
        }
        
        logger.info(
            "Platform analytics completed",
            task_id=self.request.id,
            processing_time=processing_time
        )
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Platform analytics task failed",
            task_id=self.request.id,
            error=str(e),
            processing_time=processing_time
        )
        raise


@celery_app.task(bind=True, name="workers.tasks.analytics.generate_weekly_report")
def generate_weekly_report_task(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate weekly analytics report."""
    start_time = time.time()
    
    try:
        report_type = report_data.get("type", "user")  # user, platform, admin
        user_id = report_data.get("user_id") if report_type == "user" else None
        
        logger.info(
            "Starting weekly report generation task",
            task_id=self.request.id,
            report_type=report_type,
            user_id=user_id
        )
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Generating weekly report", "progress": 10}
        )
        
        # Calculate week range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Fetching weekly data", "progress": 30}
        )
        
        # Generate report based on type
        if report_type == "user":
            mock_data = _generate_mock_user_data(user_id, start_date, end_date)
            report_content = _generate_user_weekly_report(mock_data, user_id)
        elif report_type == "platform":
            mock_data = _generate_mock_platform_data(start_date, end_date)
            report_content = _generate_platform_weekly_report(mock_data)
        else:
            mock_data = _generate_mock_admin_data(start_date, end_date)
            report_content = _generate_admin_weekly_report(mock_data)
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Generating report content", "progress": 80}
        )
        
        processing_time = time.time() - start_time
        
        result = {
            "task_id": self.request.id,
            "report_type": report_type,
            "user_id": user_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "report_content": report_content,
            "processing_time": processing_time,
            "status": "completed",
            "timestamp": time.time()
        }
        
        logger.info(
            "Weekly report generated",
            task_id=self.request.id,
            report_type=report_type,
            processing_time=processing_time
        )
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Weekly report generation failed",
            task_id=self.request.id,
            error=str(e),
            processing_time=processing_time
        )
        raise


@celery_app.task(bind=True, name="workers.tasks.analytics.cleanup_old_analytics")
def cleanup_old_analytics_task(self, days_old: int = 90) -> Dict[str, Any]:
    """Clean up old analytics data."""
    start_time = time.time()
    
    try:
        logger.info(
            "Starting analytics cleanup task",
            task_id=self.request.id,
            days_old=days_old
        )
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Cleaning up old analytics", "progress": 10}
        )
        
        # In a real implementation, you would:
        # 1. Query the database for old analytics data
        # 2. Delete them in batches
        # 3. Update related records
        
        # For now, we'll simulate the cleanup
        import time
        time.sleep(2)  # Simulate work
        
        processing_time = time.time() - start_time
        
        result = {
            "task_id": self.request.id,
            "days_old": days_old,
            "records_cleaned": 0,  # Would be actual count
            "processing_time": processing_time,
            "status": "completed",
            "timestamp": time.time()
        }
        
        logger.info(
            "Analytics cleanup completed",
            task_id=self.request.id,
            processing_time=processing_time
        )
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Analytics cleanup failed",
            task_id=self.request.id,
            error=str(e),
            processing_time=processing_time
        )
        raise


def _generate_mock_user_data(user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Generate mock user data for analytics."""
    # Simulate user activity data
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = {
        "user_id": user_id,
        "sessions": [],
        "scoring_results": [],
        "practice_sessions": []
    }
    
    # Generate mock sessions
    for date in dates:
        if np.random.random() > 0.3:  # 70% chance of activity
            data["sessions"].append({
                "date": date.isoformat(),
                "duration": np.random.randint(300, 3600),  # 5-60 minutes
                "module": np.random.choice(["speaking", "writing", "listening", "reading"]),
                "score": np.random.uniform(4.0, 9.0)
            })
    
    # Generate mock scoring results
    for _ in range(np.random.randint(5, 20)):
        data["scoring_results"].append({
            "date": np.random.choice(dates).isoformat(),
            "task_type": np.random.choice(["writing_task_1", "writing_task_2", "speaking_part_1"]),
            "band_score": np.random.uniform(4.0, 9.0),
            "confidence": np.random.uniform(0.7, 0.95)
        })
    
    return data


def _generate_mock_platform_data(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Generate mock platform data for analytics."""
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = {
        "daily_stats": [],
        "user_registrations": [],
        "scoring_activity": []
    }
    
    # Generate daily stats
    for date in dates:
        data["daily_stats"].append({
            "date": date.isoformat(),
            "active_users": np.random.randint(50, 500),
            "total_sessions": np.random.randint(100, 1000),
            "total_scorings": np.random.randint(50, 300)
        })
    
    # Generate user registrations
    for date in dates:
        registrations = np.random.randint(5, 50)
        data["user_registrations"].append({
            "date": date.isoformat(),
            "count": registrations
        })
    
    # Generate scoring activity
    for date in dates:
        data["scoring_activity"].append({
            "date": date.isoformat(),
            "writing_task_1": np.random.randint(10, 100),
            "writing_task_2": np.random.randint(20, 150),
            "speaking_part_1": np.random.randint(15, 80),
            "speaking_part_2": np.random.randint(10, 60),
            "speaking_part_3": np.random.randint(5, 40)
        })
    
    return data


def _process_user_analytics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process user analytics data."""
    sessions = data.get("sessions", [])
    scoring_results = data.get("scoring_results", [])
    
    if not sessions and not scoring_results:
        return {"error": "No data available"}
    
    # Calculate session statistics
    session_durations = [s["duration"] for s in sessions]
    session_modules = [s["module"] for s in sessions]
    
    # Calculate scoring statistics
    band_scores = [s["band_score"] for s in scoring_results]
    task_types = [s["task_type"] for s in scoring_results]
    
    analytics = {
        "total_sessions": len(sessions),
        "total_scorings": len(scoring_results),
        "avg_session_duration": np.mean(session_durations) if session_durations else 0,
        "avg_band_score": np.mean(band_scores) if band_scores else 0,
        "module_distribution": pd.Series(session_modules).value_counts().to_dict(),
        "task_type_distribution": pd.Series(task_types).value_counts().to_dict(),
        "score_progression": _calculate_score_progression(scoring_results),
        "activity_trend": _calculate_activity_trend(sessions)
    }
    
    return analytics


def _process_platform_analytics(data: Dict[str, Any], metrics: List[str]) -> Dict[str, Any]:
    """Process platform analytics data."""
    daily_stats = data.get("daily_stats", [])
    user_registrations = data.get("user_registrations", [])
    scoring_activity = data.get("scoring_activity", [])
    
    analytics = {}
    
    if "users" in metrics:
        analytics["user_metrics"] = {
            "total_active_users": sum(s["active_users"] for s in daily_stats),
            "avg_daily_active_users": np.mean([s["active_users"] for s in daily_stats]),
            "total_registrations": sum(r["count"] for r in user_registrations),
            "registration_trend": [r["count"] for r in user_registrations]
        }
    
    if "sessions" in metrics:
        analytics["session_metrics"] = {
            "total_sessions": sum(s["total_sessions"] for s in daily_stats),
            "avg_daily_sessions": np.mean([s["total_sessions"] for s in daily_stats]),
            "session_trend": [s["total_sessions"] for s in daily_stats]
        }
    
    if "scoring" in metrics:
        analytics["scoring_metrics"] = {
            "total_scorings": sum(s["total_scorings"] for s in daily_stats),
            "avg_daily_scorings": np.mean([s["total_scorings"] for s in daily_stats]),
            "scoring_by_task_type": _aggregate_scoring_by_task_type(scoring_activity)
        }
    
    return analytics


def _generate_user_charts(data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Generate charts for user analytics."""
    sessions = data.get("sessions", [])
    scoring_results = data.get("scoring_results", [])
    
    charts = {}
    
    if sessions:
        # Session duration trend
        df_sessions = pd.DataFrame(sessions)
        df_sessions['date'] = pd.to_datetime(df_sessions['date'])
        
        fig = px.line(df_sessions, x='date', y='duration', 
                     title=f'Session Duration Trend - User {user_id}')
        charts["session_duration_trend"] = fig.to_json()
    
    if scoring_results:
        # Band score progression
        df_scoring = pd.DataFrame(scoring_results)
        df_scoring['date'] = pd.to_datetime(df_scoring['date'])
        
        fig = px.scatter(df_scoring, x='date', y='band_score', color='task_type',
                        title=f'Band Score Progression - User {user_id}')
        charts["band_score_progression"] = fig.to_json()
    
    return charts


def _generate_platform_charts(data: Dict[str, Any], metrics: List[str]) -> Dict[str, Any]:
    """Generate charts for platform analytics."""
    daily_stats = data.get("daily_stats", [])
    user_registrations = data.get("user_registrations", [])
    scoring_activity = data.get("scoring_activity", [])
    
    charts = {}
    
    if daily_stats:
        df_stats = pd.DataFrame(daily_stats)
        df_stats['date'] = pd.to_datetime(df_stats['date'])
        
        # Daily active users
        fig = px.line(df_stats, x='date', y='active_users',
                     title='Daily Active Users')
        charts["daily_active_users"] = fig.to_json()
        
        # Daily sessions
        fig = px.line(df_stats, x='date', y='total_sessions',
                     title='Daily Sessions')
        charts["daily_sessions"] = fig.to_json()
    
    if user_registrations:
        df_registrations = pd.DataFrame(user_registrations)
        df_registrations['date'] = pd.to_datetime(df_registrations['date'])
        
        fig = px.bar(df_registrations, x='date', y='count',
                    title='Daily User Registrations')
        charts["daily_registrations"] = fig.to_json()
    
    return charts


def _calculate_score_progression(scoring_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate score progression over time."""
    if not scoring_results:
        return {}
    
    df = pd.DataFrame(scoring_results)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Calculate moving average
    df['moving_avg'] = df['band_score'].rolling(window=3, min_periods=1).mean()
    
    return {
        "trend": df['moving_avg'].tolist(),
        "dates": df['date'].dt.strftime('%Y-%m-%d').tolist(),
        "improvement": df['band_score'].iloc[-1] - df['band_score'].iloc[0] if len(df) > 1 else 0
    }


def _calculate_activity_trend(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate activity trend over time."""
    if not sessions:
        return {}
    
    df = pd.DataFrame(sessions)
    df['date'] = pd.to_datetime(df['date'])
    daily_activity = df.groupby('date').size().reset_index(name='sessions')
    
    return {
        "daily_sessions": daily_activity['sessions'].tolist(),
        "dates": daily_activity['date'].dt.strftime('%Y-%m-%d').tolist(),
        "total_sessions": len(sessions)
    }


def _aggregate_scoring_by_task_type(scoring_activity: List[Dict[str, Any]]) -> Dict[str, int]:
    """Aggregate scoring activity by task type."""
    if not scoring_activity:
        return {}
    
    totals = {}
    for activity in scoring_activity:
        for task_type, count in activity.items():
            if task_type != "date":
                totals[task_type] = totals.get(task_type, 0) + count
    
    return totals


def _generate_mock_admin_data(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Generate mock admin data."""
    return {
        "system_health": {
            "uptime": 99.8,
            "error_rate": 0.2,
            "response_time": 150
        },
        "resource_usage": {
            "cpu": 45.2,
            "memory": 67.8,
            "disk": 23.4
        }
    }


def _generate_user_weekly_report(data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Generate weekly report for a user."""
    analytics = _process_user_analytics(data)
    
    return {
        "user_id": user_id,
        "period": "weekly",
        "summary": {
            "total_sessions": analytics.get("total_sessions", 0),
            "total_scorings": analytics.get("total_scorings", 0),
            "avg_band_score": round(analytics.get("avg_band_score", 0), 2),
            "improvement": analytics.get("score_progression", {}).get("improvement", 0)
        },
        "recommendations": [
            "Continue practicing writing tasks to improve coherence",
            "Focus on speaking fluency in Part 2",
            "Review grammar patterns for better accuracy"
        ]
    }


def _generate_platform_weekly_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate weekly report for the platform."""
    analytics = _process_platform_analytics(data, ["users", "sessions", "scoring"])
    
    return {
        "period": "weekly",
        "summary": {
            "total_active_users": analytics.get("user_metrics", {}).get("total_active_users", 0),
            "total_sessions": analytics.get("session_metrics", {}).get("total_sessions", 0),
            "total_scorings": analytics.get("scoring_metrics", {}).get("total_scorings", 0)
        },
        "trends": {
            "user_growth": "positive",
            "engagement": "stable",
            "scoring_activity": "increasing"
        }
    }


def _generate_admin_weekly_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate weekly report for admin."""
    return {
        "period": "weekly",
        "system_health": data.get("system_health", {}),
        "resource_usage": data.get("resource_usage", {}),
        "alerts": [],
        "recommendations": [
            "Monitor memory usage as it approaches 70%",
            "Consider scaling up during peak hours",
            "Review error logs for potential issues"
        ]
    }
