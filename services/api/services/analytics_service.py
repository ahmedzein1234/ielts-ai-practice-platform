"""
Analytics Service for Advanced Analytics & Reporting (Phase 4).
Implements comprehensive analytics tracking, predictive modeling, and reporting capabilities.
"""

import structlog
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc, text
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.cluster import KMeans
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

from ..models.analytics import (
    AnalyticsEvent, PerformanceMetric, PredictiveModel, ComparativeAnalysis,
    CustomReport, ReportExecution, AnalyticsDashboard, DataExport,
    AnalyticsEventType, ReportType, VisualizationType
)
from ..models.assessment import TestSession, TestStatus
from ..models.content import ContentItem, ContentType
from ..models.learning import LearningPath, UserProgress, SkillMastery
from ..models.user import User
from ..schemas.analytics import (
    AnalyticsEventCreate, PerformanceMetricCreate, PredictiveModelCreate,
    ComparativeAnalysisCreate, CustomReportCreate, AnalyticsDashboardCreate,
    DataExportCreate, AnalyticsEventSearchParams, PerformanceMetricSearchParams,
    PredictiveModelSearchParams, CustomReportSearchParams, DataExportSearchParams,
    TrendAnalysis, CorrelationAnalysis, AnomalyDetection, PredictiveInsight,
    ComparativeInsight, ReportGenerationRequest, ExportConfiguration,
    AnalyticsSummary, RealTimeMetric, RealTimeDashboard
)

logger = structlog.get_logger(__name__)

class AnalyticsService:
    """Service for managing advanced analytics and reporting."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Analytics Event Tracking
    def track_event(self, user_id: str, event_data: AnalyticsEventCreate) -> AnalyticsEvent:
        """Track an analytics event."""
        try:
            event = AnalyticsEvent(
                id=str(uuid.uuid4()),
                user_id=user_id,
                session_id=event_data.session_id,
                event_type=event_data.event_type,
                event_name=event_data.event_name,
                event_data=event_data.event_data,
                page_url=event_data.page_url,
                referrer=event_data.referrer,
                user_agent=event_data.user_agent,
                ip_address=event_data.ip_address,
                device_type=event_data.device_type,
                browser=event_data.browser,
                os=event_data.os,
                screen_resolution=event_data.screen_resolution,
                duration_ms=event_data.duration_ms
            )
            
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            
            logger.info("Analytics event tracked successfully", 
                       user_id=user_id, event_type=event_data.event_type.value)
            return event
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to track analytics event", 
                        user_id=user_id, error=str(e))
            raise
    
    def get_user_events(self, user_id: str, params: AnalyticsEventSearchParams) -> List[AnalyticsEvent]:
        """Get analytics events for a user with filtering."""
        query = self.db.query(AnalyticsEvent).filter(AnalyticsEvent.user_id == user_id)
        
        if params.event_type:
            query = query.filter(AnalyticsEvent.event_type == params.event_type)
        
        if params.event_name:
            query = query.filter(AnalyticsEvent.event_name.ilike(f"%{params.event_name}%"))
        
        if params.page_url:
            query = query.filter(AnalyticsEvent.page_url.ilike(f"%{params.page_url}%"))
        
        if params.device_type:
            query = query.filter(AnalyticsEvent.device_type == params.device_type)
        
        if params.browser:
            query = query.filter(AnalyticsEvent.browser == params.browser)
        
        if params.start_date:
            query = query.filter(AnalyticsEvent.timestamp >= params.start_date)
        
        if params.end_date:
            query = query.filter(AnalyticsEvent.timestamp <= params.end_date)
        
        return query.order_by(desc(AnalyticsEvent.timestamp)).offset(params.offset).limit(params.limit).all()
    
    # Performance Metrics
    def record_metric(self, user_id: str, metric_data: PerformanceMetricCreate) -> PerformanceMetric:
        """Record a performance metric."""
        try:
            metric = PerformanceMetric(
                id=str(uuid.uuid4()),
                user_id=user_id,
                metric_name=metric_data.metric_name,
                metric_value=metric_data.metric_value,
                metric_unit=metric_data.metric_unit,
                module_type=metric_data.module_type,
                skill_area=metric_data.skill_area,
                difficulty_level=metric_data.difficulty_level,
                metadata=metric_data.metadata
            )
            
            self.db.add(metric)
            self.db.commit()
            self.db.refresh(metric)
            
            logger.info("Performance metric recorded successfully", 
                       user_id=user_id, metric_name=metric_data.metric_name)
            return metric
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to record performance metric", 
                        user_id=user_id, error=str(e))
            raise
    
    def get_user_metrics(self, user_id: str, params: PerformanceMetricSearchParams) -> List[PerformanceMetric]:
        """Get performance metrics for a user with filtering."""
        query = self.db.query(PerformanceMetric).filter(PerformanceMetric.user_id == user_id)
        
        if params.metric_name:
            query = query.filter(PerformanceMetric.metric_name.ilike(f"%{params.metric_name}%"))
        
        if params.module_type:
            query = query.filter(PerformanceMetric.module_type == params.module_type)
        
        if params.skill_area:
            query = query.filter(PerformanceMetric.skill_area == params.skill_area)
        
        if params.difficulty_level:
            query = query.filter(PerformanceMetric.difficulty_level == params.difficulty_level)
        
        if params.min_value is not None:
            query = query.filter(PerformanceMetric.metric_value >= params.min_value)
        
        if params.max_value is not None:
            query = query.filter(PerformanceMetric.metric_value <= params.max_value)
        
        if params.start_date:
            query = query.filter(PerformanceMetric.recorded_at >= params.start_date)
        
        if params.end_date:
            query = query.filter(PerformanceMetric.recorded_at <= params.end_date)
        
        return query.order_by(desc(PerformanceMetric.recorded_at)).offset(params.offset).limit(params.limit).all()
    
    # Analytics Summary
    def get_analytics_summary(self, user_id: str) -> AnalyticsSummary:
        """Get analytics summary for a user."""
        try:
            # Count different types of data
            total_events = self.db.query(AnalyticsEvent).filter(
                AnalyticsEvent.user_id == user_id
            ).count()
            
            total_metrics = self.db.query(PerformanceMetric).filter(
                PerformanceMetric.user_id == user_id
            ).count()
            
            total_predictions = self.db.query(PredictiveModel).filter(
                PredictiveModel.user_id == user_id
            ).count()
            
            total_reports = self.db.query(CustomReport).filter(
                CustomReport.user_id == user_id
            ).count()
            
            total_exports = self.db.query(DataExport).filter(
                DataExport.user_id == user_id
            ).count()
            
            # Get recent activity
            recent_events = self.db.query(AnalyticsEvent).filter(
                AnalyticsEvent.user_id == user_id
            ).order_by(desc(AnalyticsEvent.timestamp)).limit(10).all()
            
            recent_activity = [
                {
                    "type": "event",
                    "timestamp": event.timestamp.isoformat(),
                    "description": f"{event.event_type.value}: {event.event_name}",
                    "data": event.event_data
                }
                for event in recent_events
            ]
            
            return AnalyticsSummary(
                total_events=total_events,
                total_metrics=total_metrics,
                total_predictions=total_predictions,
                total_reports=total_reports,
                total_exports=total_exports,
                recent_activity=recent_activity
            )
            
        except Exception as e:
            logger.error("Failed to get analytics summary", user_id=user_id, error=str(e))
            raise
    
    # Advanced Analytics Methods
    def analyze_trends(self, user_id: str, metric_name: str, days: int = 30) -> TrendAnalysis:
        """Analyze trends for a specific metric."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get metric data
            metrics = self.db.query(PerformanceMetric).filter(
                and_(
                    PerformanceMetric.user_id == user_id,
                    PerformanceMetric.metric_name == metric_name,
                    PerformanceMetric.recorded_at >= start_date,
                    PerformanceMetric.recorded_at <= end_date
                )
            ).order_by(PerformanceMetric.recorded_at).all()
            
            if len(metrics) < 2:
                return TrendAnalysis(
                    metric_name=metric_name,
                    trend_direction="stable",
                    change_percentage=0.0,
                    time_period=f"{days} days",
                    data_points=[]
                )
            
            # Calculate trend
            values = [m.metric_value for m in metrics]
            dates = [m.recorded_at for m in metrics]
            
            # Linear regression for trend analysis
            x_values = [float((d - dates[0]).days) for d in dates]
            y_values = [float(v) for v in values]
            x = np.array(x_values).reshape(-1, 1)
            y = np.array(y_values)
            
            model = LinearRegression()
            model.fit(x, y)
            
            slope = model.coef_[0]
            first_value = values[0]
            last_value = values[-1]
            
            if first_value != 0:
                change_percentage = ((last_value - first_value) / first_value) * 100
            else:
                change_percentage = 0.0
            
            # Determine trend direction
            if slope > 0.01:
                trend_direction = "increasing"
            elif slope < -0.01:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
            
            # Prepare data points
            data_points = [
                {
                    "date": date.isoformat(),
                    "value": value,
                    "day": (date - dates[0]).days
                }
                for date, value in zip(dates, values)
            ]
            
            return TrendAnalysis(
                metric_name=metric_name,
                trend_direction=trend_direction,
                change_percentage=change_percentage,
                time_period=f"{days} days",
                data_points=data_points
            )
            
        except Exception as e:
            logger.error("Failed to analyze trends", user_id=user_id, metric_name=metric_name, error=str(e))
            raise
    
    def analyze_correlations(self, user_id: str, variable1: str, variable2: str, days: int = 30) -> CorrelationAnalysis:
        """Analyze correlation between two variables."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get data for both variables
            metrics1 = self.db.query(PerformanceMetric).filter(
                and_(
                    PerformanceMetric.user_id == user_id,
                    PerformanceMetric.metric_name == variable1,
                    PerformanceMetric.recorded_at >= start_date,
                    PerformanceMetric.recorded_at <= end_date
                )
            ).all()
            
            metrics2 = self.db.query(PerformanceMetric).filter(
                and_(
                    PerformanceMetric.user_id == user_id,
                    PerformanceMetric.metric_name == variable2,
                    PerformanceMetric.recorded_at >= start_date,
                    PerformanceMetric.recorded_at <= end_date
                )
            ).all()
            
            if len(metrics1) < 3 or len(metrics2) < 3:
                return CorrelationAnalysis(
                    variable1=variable1,
                    variable2=variable2,
                    correlation_coefficient=0.0,
                    significance_level=1.0,
                    sample_size=0,
                    interpretation="Insufficient data for correlation analysis"
                )
            
            # Align data by date (nearest neighbor)
            data1 = {m.recorded_at.date(): m.metric_value for m in metrics1}
            data2 = {m.recorded_at.date(): m.metric_value for m in metrics2}
            
            # Find common dates
            common_dates = set(data1.keys()) & set(data2.keys())
            
            if len(common_dates) < 3:
                return CorrelationAnalysis(
                    variable1=variable1,
                    variable2=variable2,
                    correlation_coefficient=0.0,
                    significance_level=1.0,
                    sample_size=0,
                    interpretation="Insufficient overlapping data for correlation analysis"
                )
            
            # Prepare aligned data
            values1 = [data1[date] for date in sorted(common_dates)]
            values2 = [data2[date] for date in sorted(common_dates)]
            
            # Calculate correlation
            values1_array = np.array([float(v) for v in values1])
            values2_array = np.array([float(v) for v in values2])
            correlation_result = stats.pearsonr(values1_array, values2_array)
            correlation_coefficient = float(correlation_result[0])
            p_value = float(correlation_result[1])
            
            # Determine significance
            if p_value < 0.001:
                significance_level = 0.001
            elif p_value < 0.01:
                significance_level = 0.01
            elif p_value < 0.05:
                significance_level = 0.05
            else:
                significance_level = p_value
            
            # Interpret correlation
            if abs(correlation_coefficient) < 0.1:
                interpretation = "Very weak correlation"
            elif abs(correlation_coefficient) < 0.3:
                interpretation = "Weak correlation"
            elif abs(correlation_coefficient) < 0.5:
                interpretation = "Moderate correlation"
            elif abs(correlation_coefficient) < 0.7:
                interpretation = "Strong correlation"
            else:
                interpretation = "Very strong correlation"
            
            if correlation_coefficient > 0:
                interpretation += " (positive)"
            else:
                interpretation += " (negative)"
            
            return CorrelationAnalysis(
                variable1=variable1,
                variable2=variable2,
                correlation_coefficient=correlation_coefficient,
                significance_level=significance_level,
                sample_size=len(common_dates),
                interpretation=interpretation
            )
            
        except Exception as e:
            logger.error("Failed to analyze correlations", user_id=user_id, error=str(e))
            raise
    
    def detect_anomalies(self, user_id: str, metric_name: str, days: int = 30) -> AnomalyDetection:
        """Detect anomalies in metric data."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get metric data
            metrics = self.db.query(PerformanceMetric).filter(
                and_(
                    PerformanceMetric.user_id == user_id,
                    PerformanceMetric.metric_name == metric_name,
                    PerformanceMetric.recorded_at >= start_date,
                    PerformanceMetric.recorded_at <= end_date
                )
            ).order_by(PerformanceMetric.recorded_at).all()
            
            if len(metrics) < 5:
                return AnomalyDetection(
                    metric_name=metric_name,
                    detected_anomalies=[],
                    threshold_value=0.0,
                    confidence_level=0.0
                )
            
            values = [m.metric_value for m in metrics]
            dates = [m.recorded_at for m in metrics]
            
            # Calculate statistics
            mean_value = np.mean(values)
            std_value = np.std(values)
            
            # Detect anomalies using z-score method
            anomalies = []
            threshold = 2.0  # 2 standard deviations
            
            for i, (date, value) in enumerate(zip(dates, values)):
                z_score = abs((value - mean_value) / std_value) if std_value > 0 else 0
                
                if z_score > threshold:
                    anomalies.append({
                        "date": date.isoformat(),
                        "value": value,
                        "z_score": z_score,
                        "deviation": value - mean_value,
                        "severity": "high" if z_score > 3 else "medium"
                    })
            
            # Calculate confidence level based on data quality
            confidence_level = min(1.0, len(metrics) / 100)  # More data = higher confidence
            
            return AnomalyDetection(
                metric_name=metric_name,
                detected_anomalies=anomalies,
                threshold_value=threshold,
                confidence_level=confidence_level
            )
            
        except Exception as e:
            logger.error("Failed to detect anomalies", user_id=user_id, metric_name=metric_name, error=str(e))
            raise
    
    def generate_predictive_insights(self, user_id: str) -> List[PredictiveInsight]:
        """Generate predictive insights for a user."""
        try:
            insights = []
            
            # Get recent performance data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=90)
            
            metrics = self.db.query(PerformanceMetric).filter(
                and_(
                    PerformanceMetric.user_id == user_id,
                    PerformanceMetric.recorded_at >= start_date
                )
            ).all()
            
            if len(metrics) < 10:
                return insights
            
            # Analyze different aspects
            metric_groups = {}
            for metric in metrics:
                if metric.metric_name not in metric_groups:
                    metric_groups[metric.metric_name] = []
                metric_groups[metric.metric_name].append(metric)
            
            # Generate insights for each metric
            for metric_name, metric_list in metric_groups.items():
                if len(metric_list) < 5:
                    continue
                
                values = [m.metric_value for m in metric_list]
                recent_values = values[-5:]  # Last 5 values
                
                # Calculate trend
                if len(recent_values) >= 2:
                    trend = (recent_values[-1] - recent_values[0]) / len(recent_values)
                    
                    # Predict future value (30 days ahead)
                    predicted_value = recent_values[-1] + (trend * 30)
                    
                    # Generate insight based on trend
                    if trend > 0:
                        insight_type = "improvement"
                        title = f"Positive Trend in {metric_name}"
                        description = f"Your {metric_name} is showing consistent improvement."
                        factors = ["Consistent practice", "Effective learning strategies"]
                        recommendations = [
                            "Continue with current study routine",
                            "Focus on maintaining momentum",
                            "Consider increasing difficulty level"
                        ]
                    elif trend < 0:
                        insight_type = "decline"
                        title = f"Declining Trend in {metric_name}"
                        description = f"Your {metric_name} has been declining recently."
                        factors = ["Reduced practice time", "Increased difficulty"]
                        recommendations = [
                            "Review recent study materials",
                            "Consider additional practice",
                            "Seek help for challenging concepts"
                        ]
                    else:
                        insight_type = "stable"
                        title = f"Stable Performance in {metric_name}"
                        description = f"Your {metric_name} has remained stable."
                        factors = ["Consistent performance", "Balanced approach"]
                        recommendations = [
                            "Maintain current study habits",
                            "Consider new challenges",
                            "Focus on other areas for improvement"
                        ]
                    
                    # Calculate confidence based on data consistency
                    confidence_score = min(0.9, len(metric_list) / 50)  # More data = higher confidence
                    
                    insights.append(PredictiveInsight(
                        insight_type=insight_type,
                        title=title,
                        description=description,
                        confidence_score=confidence_score,
                        predicted_value=predicted_value,
                        target_date=end_date + timedelta(days=30),
                        factors=factors,
                        recommendations=recommendations
                    ))
            
            return insights
            
        except Exception as e:
            logger.error("Failed to generate predictive insights", user_id=user_id, error=str(e))
            raise
    
    def generate_comparative_analysis(self, user_id: str, analysis_type: str, comparison_group: str) -> ComparativeAnalysis:
        """Generate comparative analysis for a user."""
        try:
            # Get user's performance data
            user_metrics = self.db.query(PerformanceMetric).filter(
                PerformanceMetric.user_id == user_id
            ).all()
            
            if not user_metrics:
                raise ValueError("No performance data available for user")
            
            # Get comparison group data (simplified - in real implementation, this would be more sophisticated)
            # For now, we'll use a sample of other users' data
            comparison_metrics = self.db.query(PerformanceMetric).filter(
                PerformanceMetric.user_id != user_id
            ).limit(100).all()
            
            if not comparison_metrics:
                raise ValueError("No comparison data available")
            
            # Calculate user's average performance
            user_values = [m.metric_value for m in user_metrics]
            user_average = np.mean(user_values)
            
            # Calculate group statistics
            group_values = [m.metric_value for m in comparison_metrics]
            group_average = np.mean(group_values)
            group_median = np.median(group_values)
            group_std_dev = np.std(group_values)
            
            # Calculate user's percentile
            user_percentile = stats.percentileofscore(group_values, user_average)
            
            # Calculate user's rank
            sorted_values = sorted(group_values, reverse=True)
            user_rank = sorted_values.index(user_average) + 1 if user_average in sorted_values else len(sorted_values)
            
            # Prepare comparison data
            comparison_data = {
                "user_average": user_average,
                "group_statistics": {
                    "mean": group_average,
                    "median": group_median,
                    "std_dev": group_std_dev,
                    "min": min(group_values),
                    "max": max(group_values)
                },
                "performance_distribution": {
                    "top_10_percent": np.percentile(group_values, 90),
                    "top_25_percent": np.percentile(group_values, 75),
                    "median": np.percentile(group_values, 50),
                    "bottom_25_percent": np.percentile(group_values, 25),
                    "bottom_10_percent": np.percentile(group_values, 10)
                }
            }
            
            analysis = ComparativeAnalysis(
                id=str(uuid.uuid4()),
                user_id=user_id,
                analysis_type=analysis_type,
                comparison_group=comparison_group,
                user_percentile=user_percentile,
                group_average=group_average,
                group_median=group_median,
                group_std_dev=group_std_dev,
                user_rank=user_rank,
                total_in_group=len(group_values),
                comparison_data=comparison_data
            )
            
            self.db.add(analysis)
            self.db.commit()
            self.db.refresh(analysis)
            
            return analysis
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to generate comparative analysis", user_id=user_id, error=str(e))
            raise
    
    def create_custom_report(self, user_id: str, report_data: CustomReportCreate) -> CustomReport:
        """Create a custom report."""
        try:
            report = CustomReport(
                id=str(uuid.uuid4()),
                user_id=user_id,
                name=report_data.name,
                description=report_data.description,
                report_type=report_data.report_type,
                filters=report_data.filters,
                metrics=report_data.metrics,
                visualizations=report_data.visualizations,
                is_scheduled=report_data.is_scheduled,
                schedule_frequency=report_data.schedule_frequency,
                export_format=report_data.export_format,
                email_recipients=report_data.email_recipients
            )
            
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            
            logger.info("Custom report created successfully", 
                       user_id=user_id, report_name=report_data.name)
            return report
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create custom report", 
                        user_id=user_id, error=str(e))
            raise
    
    def get_user_reports(self, user_id: str, params: CustomReportSearchParams) -> List[CustomReport]:
        """Get custom reports for a user with filtering."""
        query = self.db.query(CustomReport).filter(CustomReport.user_id == user_id)
        
        if params.report_type:
            query = query.filter(CustomReport.report_type == params.report_type)
        
        if params.is_scheduled is not None:
            query = query.filter(CustomReport.is_scheduled == params.is_scheduled)
        
        if params.is_active is not None:
            query = query.filter(CustomReport.is_active == params.is_active)
        
        if params.name:
            query = query.filter(CustomReport.name.ilike(f"%{params.name}%"))
        
        if params.created_after:
            query = query.filter(CustomReport.created_at >= params.created_after)
        
        if params.created_before:
            query = query.filter(CustomReport.created_at <= params.created_before)
        
        return query.order_by(desc(CustomReport.created_at)).offset(params.offset).limit(params.limit).all()
    
    def execute_report(self, report_id: str) -> ReportExecution:
        """Execute a custom report."""
        try:
            report = self.db.query(CustomReport).filter(CustomReport.id == report_id).first()
            if not report:
                raise ValueError("Report not found")
            
            # Create execution record
            execution = ReportExecution(
                id=str(uuid.uuid4()),
                custom_report_id=report_id,
                status="running",
                started_at=datetime.utcnow()
            )
            
            self.db.add(execution)
            self.db.commit()
            
            # Simulate report generation (in real implementation, this would be async)
            try:
                # Generate report data based on configuration
                data_points = self._generate_report_data(report)
                
                # Update execution record
                execution.status = "completed"
                execution.completed_at = datetime.utcnow()
                execution.data_points = data_points
                execution.file_size_bytes = len(str(data_points)) * 8  # Rough estimate
                execution.file_url = f"/reports/{execution.id}/download"
                
                # Update report last generated
                report.last_generated = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(execution)
                
                logger.info("Report executed successfully", report_id=report_id, execution_id=execution.id)
                return execution
                
            except Exception as e:
                execution.status = "failed"
                execution.completed_at = datetime.utcnow()
                execution.error_message = str(e)
                execution.error_details = {"error_type": type(e).__name__}
                
                self.db.commit()
                self.db.refresh(execution)
                
                logger.error("Report execution failed", report_id=report_id, error=str(e))
                return execution
                
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to execute report", report_id=report_id, error=str(e))
            raise
    
    def _generate_report_data(self, report: CustomReport) -> int:
        """Generate data for a custom report."""
        # This is a simplified implementation
        # In a real system, this would query the database based on report configuration
        
        # Simulate data generation based on report type
        if report.report_type == ReportType.USER_PROGRESS:
            return 150  # Simulate 150 data points
        elif report.report_type == ReportType.PERFORMANCE_ANALYSIS:
            return 200
        elif report.report_type == ReportType.ENGAGEMENT_METRICS:
            return 100
        else:
            return 50
    
    def create_dashboard(self, user_id: str, dashboard_data: AnalyticsDashboardCreate) -> AnalyticsDashboard:
        """Create an analytics dashboard."""
        try:
            dashboard = AnalyticsDashboard(
                id=str(uuid.uuid4()),
                user_id=user_id,
                name=dashboard_data.name,
                description=dashboard_data.description,
                is_default=dashboard_data.is_default,
                layout_config=dashboard_data.layout_config,
                widget_configs=dashboard_data.widget_configs,
                default_filters=dashboard_data.default_filters,
                refresh_interval=dashboard_data.refresh_interval
            )
            
            # If this is set as default, unset other default dashboards
            if dashboard_data.is_default:
                self.db.query(AnalyticsDashboard).filter(
                    and_(
                        AnalyticsDashboard.user_id == user_id,
                        AnalyticsDashboard.is_default == True
                    )
                ).update({"is_default": False})
            
            self.db.add(dashboard)
            self.db.commit()
            self.db.refresh(dashboard)
            
            logger.info("Analytics dashboard created successfully", 
                       user_id=user_id, dashboard_name=dashboard_data.name)
            return dashboard
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create analytics dashboard", 
                        user_id=user_id, error=str(e))
            raise
    
    def get_user_dashboards(self, user_id: str) -> List[AnalyticsDashboard]:
        """Get analytics dashboards for a user."""
        return self.db.query(AnalyticsDashboard).filter(
            AnalyticsDashboard.user_id == user_id
        ).order_by(desc(AnalyticsDashboard.is_default), desc(AnalyticsDashboard.created_at)).all()
    
    def create_data_export(self, user_id: str, export_data: DataExportCreate) -> DataExport:
        """Create a data export request."""
        try:
            export = DataExport(
                id=str(uuid.uuid4()),
                user_id=user_id,
                export_type=export_data.export_type,
                format=export_data.format,
                filters=export_data.filters,
                fields=export_data.fields,
                date_range=export_data.date_range,
                status="pending",
                progress_percentage=0.0
            )
            
            self.db.add(export)
            self.db.commit()
            self.db.refresh(export)
            
            logger.info("Data export created successfully", 
                       user_id=user_id, export_type=export_data.export_type)
            return export
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create data export", 
                        user_id=user_id, error=str(e))
            raise
    
    def get_user_exports(self, user_id: str, params: DataExportSearchParams) -> List[DataExport]:
        """Get data exports for a user with filtering."""
        query = self.db.query(DataExport).filter(DataExport.user_id == user_id)
        
        if params.export_type:
            query = query.filter(DataExport.export_type == params.export_type)
        
        if params.format:
            query = query.filter(DataExport.format == params.format)
        
        if params.status:
            query = query.filter(DataExport.status == params.status)
        
        if params.requested_after:
            query = query.filter(DataExport.requested_at >= params.requested_after)
        
        if params.requested_before:
            query = query.filter(DataExport.requested_at <= params.requested_before)
        
        return query.order_by(desc(DataExport.requested_at)).offset(params.offset).limit(params.limit).all()
    
    def get_real_time_metrics(self, user_id: str) -> List[RealTimeMetric]:
        """Get real-time metrics for a user."""
        try:
            metrics = []
            
            # Get recent performance metrics
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(hours=24)
            
            recent_metrics = self.db.query(PerformanceMetric).filter(
                and_(
                    PerformanceMetric.user_id == user_id,
                    PerformanceMetric.recorded_at >= start_date
                )
            ).all()
            
            # Group by metric name
            metric_groups = {}
            for metric in recent_metrics:
                if metric.metric_name not in metric_groups:
                    metric_groups[metric.metric_name] = []
                metric_groups[metric.metric_name].append(metric)
            
            # Calculate real-time metrics
            for metric_name, metric_list in metric_groups.items():
                if len(metric_list) < 2:
                    continue
                
                # Sort by timestamp
                sorted_metrics = sorted(metric_list, key=lambda x: x.recorded_at)
                
                current_value = sorted_metrics[-1].metric_value
                previous_value = sorted_metrics[-2].metric_value if len(sorted_metrics) > 1 else current_value
                
                # Calculate change percentage
                if previous_value != 0:
                    change_percentage = ((current_value - previous_value) / previous_value) * 100
                else:
                    change_percentage = 0.0
                
                # Determine trend
                if change_percentage > 5:
                    trend = "increasing"
                elif change_percentage < -5:
                    trend = "decreasing"
                else:
                    trend = "stable"
                
                metrics.append(RealTimeMetric(
                    metric_name=metric_name,
                    current_value=current_value,
                    previous_value=previous_value,
                    change_percentage=change_percentage,
                    trend=trend,
                    last_updated=sorted_metrics[-1].recorded_at
                ))
            
            return metrics
            
        except Exception as e:
            logger.error("Failed to get real-time metrics", user_id=user_id, error=str(e))
            raise
