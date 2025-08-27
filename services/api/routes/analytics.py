"""
FastAPI routes for Advanced Analytics & Reporting (Phase 4).
Includes endpoints for analytics tracking, predictive modeling, and reporting.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
import structlog

from ..models.analytics import AnalyticsEvent, PerformanceMetric, PredictiveModel, ComparativeAnalysis, CustomReport, AnalyticsDashboard, DataExport, AnalyticsEventType, ReportType

from ..database import get_db
from ..auth import get_current_user
from ..models.user import User
from ..services.analytics_service import AnalyticsService
from ..schemas.analytics import (
    AnalyticsEventCreate, AnalyticsEventResponse, AnalyticsEventUpdate, AnalyticsEventSearchParams,
    PerformanceMetricCreate, PerformanceMetricResponse, PerformanceMetricUpdate, PerformanceMetricSearchParams,
    PredictiveModelCreate, PredictiveModelResponse, PredictiveModelUpdate, PredictiveModelSearchParams,
    ComparativeAnalysisCreate, ComparativeAnalysisResponse, ComparativeAnalysisUpdate,
    CustomReportCreate, CustomReportResponse, CustomReportUpdate, CustomReportSearchParams,
    AnalyticsDashboardCreate, AnalyticsDashboardResponse, AnalyticsDashboardUpdate,
    DataExportCreate, DataExportResponse, DataExportSearchParams,
    AnalyticsSummary, TrendAnalysis, CorrelationAnalysis, AnomalyDetection, PredictiveInsight,
    ComparativeInsight, ReportGenerationRequest, ExportConfiguration, RealTimeMetric
)

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])

# Helper function for role-based access
def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role.value != required_role and current_user.role.value != "admin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# Analytics Event Tracking
@router.post("/events", response_model=AnalyticsEventResponse)
async def track_event(
    event_data: AnalyticsEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track an analytics event."""
    try:
        analytics_service = AnalyticsService(db)
        event = analytics_service.track_event(current_user.id, event_data)
        return event
    except Exception as e:
        logger.error("Failed to track analytics event", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to track analytics event")

@router.get("/events", response_model=List[AnalyticsEventResponse])
async def get_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    event_name: Optional[str] = Query(None, description="Filter by event name"),
    page_url: Optional[str] = Query(None, description="Filter by page URL"),
    device_type: Optional[str] = Query(None, description="Filter by device type"),
    browser: Optional[str] = Query(None, description="Filter by browser"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics events for the current user with filtering."""
    try:
        from datetime import datetime
        
        params = AnalyticsEventSearchParams(
            event_type=AnalyticsEventType(event_type) if event_type else None,
            event_name=event_name,
            page_url=page_url,
            device_type=device_type,
            browser=browser,
            start_date=datetime.fromisoformat(start_date) if start_date else None,
            end_date=datetime.fromisoformat(end_date) if end_date else None,
            limit=limit,
            offset=offset
        )
        
        analytics_service = AnalyticsService(db)
        events = analytics_service.get_user_events(current_user.id, params)
        return events
    except Exception as e:
        logger.error("Failed to get analytics events", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get analytics events")

# Performance Metrics
@router.post("/metrics", response_model=PerformanceMetricResponse)
async def record_metric(
    metric_data: PerformanceMetricCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a performance metric."""
    try:
        analytics_service = AnalyticsService(db)
        metric = analytics_service.record_metric(current_user.id, metric_data)
        return metric
    except Exception as e:
        logger.error("Failed to record performance metric", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to record performance metric")

@router.get("/metrics", response_model=List[PerformanceMetricResponse])
async def get_metrics(
    metric_name: Optional[str] = Query(None, description="Filter by metric name"),
    module_type: Optional[str] = Query(None, description="Filter by module type"),
    skill_area: Optional[str] = Query(None, description="Filter by skill area"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    min_value: Optional[float] = Query(None, description="Minimum metric value"),
    max_value: Optional[float] = Query(None, description="Maximum metric value"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance metrics for the current user with filtering."""
    try:
        from datetime import datetime
        
        params = PerformanceMetricSearchParams(
            metric_name=metric_name,
            module_type=module_type,
            skill_area=skill_area,
            difficulty_level=difficulty_level,
            min_value=min_value,
            max_value=max_value,
            start_date=datetime.fromisoformat(start_date) if start_date else None,
            end_date=datetime.fromisoformat(end_date) if end_date else None,
            limit=limit,
            offset=offset
        )
        
        analytics_service = AnalyticsService(db)
        metrics = analytics_service.get_user_metrics(current_user.id, params)
        return metrics
    except Exception as e:
        logger.error("Failed to get performance metrics", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")

# Analytics Summary
@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics summary for the current user."""
    try:
        analytics_service = AnalyticsService(db)
        summary = analytics_service.get_analytics_summary(current_user.id)
        return summary
    except Exception as e:
        logger.error("Failed to get analytics summary", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get analytics summary")

# Advanced Analytics
@router.get("/trends/{metric_name}", response_model=TrendAnalysis)
async def analyze_trends(
    metric_name: str,
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze trends for a specific metric."""
    try:
        analytics_service = AnalyticsService(db)
        trend_analysis = analytics_service.analyze_trends(current_user.id, metric_name, days)
        return trend_analysis
    except Exception as e:
        logger.error("Failed to analyze trends", user_id=current_user.id, metric_name=metric_name, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to analyze trends")

@router.get("/correlations", response_model=CorrelationAnalysis)
async def analyze_correlations(
    variable1: str = Query(..., description="First variable name"),
    variable2: str = Query(..., description="Second variable name"),
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze correlation between two variables."""
    try:
        analytics_service = AnalyticsService(db)
        correlation_analysis = analytics_service.analyze_correlations(current_user.id, variable1, variable2, days)
        return correlation_analysis
    except Exception as e:
        logger.error("Failed to analyze correlations", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to analyze correlations")

@router.get("/anomalies/{metric_name}", response_model=AnomalyDetection)
async def detect_anomalies(
    metric_name: str,
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Detect anomalies in metric data."""
    try:
        analytics_service = AnalyticsService(db)
        anomaly_detection = analytics_service.detect_anomalies(current_user.id, metric_name, days)
        return anomaly_detection
    except Exception as e:
        logger.error("Failed to detect anomalies", user_id=current_user.id, metric_name=metric_name, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to detect anomalies")

@router.get("/insights/predictive", response_model=List[PredictiveInsight])
async def get_predictive_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get predictive insights for the current user."""
    try:
        analytics_service = AnalyticsService(db)
        insights = analytics_service.generate_predictive_insights(current_user.id)
        return insights
    except Exception as e:
        logger.error("Failed to get predictive insights", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get predictive insights")

# Comparative Analysis
@router.post("/comparative", response_model=ComparativeAnalysisResponse)
async def generate_comparative_analysis(
    analysis_data: ComparativeAnalysisCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate comparative analysis for the current user."""
    try:
        analytics_service = AnalyticsService(db)
        analysis = analytics_service.generate_comparative_analysis(
            current_user.id, 
            analysis_data.analysis_type, 
            analysis_data.comparison_group
        )
        return analysis
    except Exception as e:
        logger.error("Failed to generate comparative analysis", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate comparative analysis")

# Custom Reports
@router.post("/reports", response_model=CustomReportResponse)
async def create_custom_report(
    report_data: CustomReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a custom report."""
    try:
        analytics_service = AnalyticsService(db)
        report = analytics_service.create_custom_report(current_user.id, report_data)
        return report
    except Exception as e:
        logger.error("Failed to create custom report", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create custom report")

@router.get("/reports", response_model=List[CustomReportResponse])
async def get_custom_reports(
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    is_scheduled: Optional[bool] = Query(None, description="Filter by scheduled status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    name: Optional[str] = Query(None, description="Filter by report name"),
    created_after: Optional[str] = Query(None, description="Created after date (ISO format)"),
    created_before: Optional[str] = Query(None, description="Created before date (ISO format)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get custom reports for the current user with filtering."""
    try:
        from datetime import datetime
        
        params = CustomReportSearchParams(
            report_type=ReportType(report_type) if report_type else None,
            is_scheduled=is_scheduled,
            is_active=is_active,
            name=name,
            created_after=datetime.fromisoformat(created_after) if created_after else None,
            created_before=datetime.fromisoformat(created_before) if created_before else None,
            limit=limit,
            offset=offset
        )
        
        analytics_service = AnalyticsService(db)
        reports = analytics_service.get_user_reports(current_user.id, params)
        return reports
    except Exception as e:
        logger.error("Failed to get custom reports", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get custom reports")

@router.post("/reports/{report_id}/execute")
async def execute_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute a custom report."""
    try:
        analytics_service = AnalyticsService(db)
        execution = analytics_service.execute_report(report_id)
        return {
            "message": f"Report execution {execution.status}",
            "execution_id": execution.id,
            "status": execution.status
        }
    except Exception as e:
        logger.error("Failed to execute report", report_id=report_id, user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to execute report")

# Analytics Dashboard
@router.post("/dashboards", response_model=AnalyticsDashboardResponse)
async def create_dashboard(
    dashboard_data: AnalyticsDashboardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create an analytics dashboard."""
    try:
        analytics_service = AnalyticsService(db)
        dashboard = analytics_service.create_dashboard(current_user.id, dashboard_data)
        return dashboard
    except Exception as e:
        logger.error("Failed to create analytics dashboard", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create analytics dashboard")

@router.get("/dashboards", response_model=List[AnalyticsDashboardResponse])
async def get_dashboards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics dashboards for the current user."""
    try:
        analytics_service = AnalyticsService(db)
        dashboards = analytics_service.get_user_dashboards(current_user.id)
        return dashboards
    except Exception as e:
        logger.error("Failed to get analytics dashboards", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get analytics dashboards")

# Data Export
@router.post("/exports", response_model=DataExportResponse)
async def create_data_export(
    export_data: DataExportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a data export request."""
    try:
        analytics_service = AnalyticsService(db)
        export = analytics_service.create_data_export(current_user.id, export_data)
        return export
    except Exception as e:
        logger.error("Failed to create data export", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create data export")

@router.get("/exports", response_model=List[DataExportResponse])
async def get_data_exports(
    export_type: Optional[str] = Query(None, description="Filter by export type"),
    format: Optional[str] = Query(None, description="Filter by export format"),
    status: Optional[str] = Query(None, description="Filter by export status"),
    requested_after: Optional[str] = Query(None, description="Requested after date (ISO format)"),
    requested_before: Optional[str] = Query(None, description="Requested before date (ISO format)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get data exports for the current user with filtering."""
    try:
        from datetime import datetime
        
        params = DataExportSearchParams(
            export_type=export_type,
            format=format,
            status=status,
            requested_after=datetime.fromisoformat(requested_after) if requested_after else None,
            requested_before=datetime.fromisoformat(requested_before) if requested_before else None,
            limit=limit,
            offset=offset
        )
        
        analytics_service = AnalyticsService(db)
        exports = analytics_service.get_user_exports(current_user.id, params)
        return exports
    except Exception as e:
        logger.error("Failed to get data exports", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get data exports")

# Real-time Analytics
@router.get("/realtime/metrics", response_model=List[RealTimeMetric])
async def get_real_time_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real-time metrics for the current user."""
    try:
        analytics_service = AnalyticsService(db)
        metrics = analytics_service.get_real_time_metrics(current_user.id)
        return metrics
    except Exception as e:
        logger.error("Failed to get real-time metrics", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get real-time metrics")

# Admin endpoints (for tutors and administrators)
@router.get("/admin/user/{user_id}/summary", response_model=AnalyticsSummary)
async def get_user_analytics_summary_admin(
    user_id: str,
    current_user: User = Depends(require_role("tutor")),
    db: Session = Depends(get_db)
):
    """Get analytics summary for a specific user (admin/tutor only)."""
    try:
        analytics_service = AnalyticsService(db)
        summary = analytics_service.get_analytics_summary(user_id)
        return summary
    except Exception as e:
        logger.error("Failed to get user analytics summary (admin)", user_id=user_id, admin_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get user analytics summary")

@router.get("/admin/user/{user_id}/events", response_model=List[AnalyticsEventResponse])
async def get_user_events_admin(
    user_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_role("tutor")),
    db: Session = Depends(get_db)
):
    """Get analytics events for a specific user (admin/tutor only)."""
    try:
        params = AnalyticsEventSearchParams(limit=limit, offset=offset)
        analytics_service = AnalyticsService(db)
        events = analytics_service.get_user_events(user_id, params)
        return events
    except Exception as e:
        logger.error("Failed to get user analytics events (admin)", user_id=user_id, admin_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get user analytics events")

@router.get("/admin/user/{user_id}/metrics", response_model=List[PerformanceMetricResponse])
async def get_user_metrics_admin(
    user_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_role("tutor")),
    db: Session = Depends(get_db)
):
    """Get performance metrics for a specific user (admin/tutor only)."""
    try:
        params = PerformanceMetricSearchParams(limit=limit, offset=offset)
        analytics_service = AnalyticsService(db)
        metrics = analytics_service.get_user_metrics(user_id, params)
        return metrics
    except Exception as e:
        logger.error("Failed to get user performance metrics (admin)", user_id=user_id, admin_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get user performance metrics")
