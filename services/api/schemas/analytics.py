"""
Pydantic schemas for Advanced Analytics & Reporting (Phase 4).
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

# Enums
class AnalyticsEventType(str, Enum):
    PAGE_VIEW = "page_view"
    FEATURE_USAGE = "feature_usage"
    CONTENT_INTERACTION = "content_interaction"
    ASSESSMENT_ATTEMPT = "assessment_attempt"
    LEARNING_ACTIVITY = "learning_activity"
    USER_ENGAGEMENT = "user_engagement"
    PERFORMANCE_MILESTONE = "performance_milestone"
    SYSTEM_ERROR = "system_error"

class ReportType(str, Enum):
    USER_PROGRESS = "user_progress"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    ENGAGEMENT_METRICS = "engagement_metrics"
    CONTENT_EFFECTIVENESS = "content_effectiveness"
    SKILL_DEVELOPMENT = "skill_development"
    PREDICTIVE_INSIGHTS = "predictive_insights"
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    CUSTOM_REPORT = "custom_report"

class VisualizationType(str, Enum):
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    RADAR_CHART = "radar_chart"
    GAUGE_CHART = "gauge_chart"
    FUNNEL_CHART = "funnel_chart"

# Base Models
class AnalyticsEventBase(BaseModel):
    event_type: AnalyticsEventType
    event_name: str = Field(..., min_length=1, max_length=255)
    event_data: Dict[str, Any] = Field(default_factory=dict)
    page_url: Optional[str] = Field(None, max_length=500)
    referrer: Optional[str] = Field(None, max_length=500)
    user_agent: Optional[str] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    device_type: Optional[str] = Field(None, max_length=50)
    browser: Optional[str] = Field(None, max_length=100)
    os: Optional[str] = Field(None, max_length=100)
    screen_resolution: Optional[str] = Field(None, max_length=50)
    duration_ms: Optional[int] = Field(None, ge=0)

class PerformanceMetricBase(BaseModel):
    metric_name: str = Field(..., min_length=1, max_length=255)
    metric_value: float
    metric_unit: Optional[str] = Field(None, max_length=50)
    module_type: Optional[str] = Field(None, max_length=100)
    skill_area: Optional[str] = Field(None, max_length=100)
    difficulty_level: Optional[str] = Field(None, max_length=50)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PredictiveModelBase(BaseModel):
    model_type: str = Field(..., min_length=1, max_length=100)
    model_version: str = Field(..., min_length=1, max_length=50)
    predicted_value: float
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    prediction_interval_lower: Optional[float] = None
    prediction_interval_upper: Optional[float] = None
    input_features: Dict[str, Any] = Field(default_factory=dict)
    target_date: Optional[datetime] = None

class ComparativeAnalysisBase(BaseModel):
    analysis_type: str = Field(..., min_length=1, max_length=100)
    comparison_group: str = Field(..., min_length=1, max_length=100)
    user_percentile: float = Field(..., ge=0.0, le=100.0)
    group_average: float
    group_median: float
    group_std_dev: float
    user_rank: int = Field(..., ge=1)
    total_in_group: int = Field(..., ge=1)
    comparison_data: Dict[str, Any] = Field(default_factory=dict)

class CustomReportBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    report_type: ReportType
    filters: Dict[str, Any] = Field(default_factory=dict)
    metrics: List[str] = Field(default_factory=list)
    visualizations: List[Dict[str, Any]] = Field(default_factory=list)
    is_scheduled: bool = False
    schedule_frequency: Optional[str] = Field(None, max_length=50)
    export_format: Optional[str] = Field(None, max_length=20)
    email_recipients: List[str] = Field(default_factory=list)

class AnalyticsDashboardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_default: bool = False
    layout_config: Dict[str, Any] = Field(default_factory=dict)
    widget_configs: List[Dict[str, Any]] = Field(default_factory=list)
    default_filters: Dict[str, Any] = Field(default_factory=dict)
    refresh_interval: Optional[int] = Field(None, ge=30, le=3600)  # 30 seconds to 1 hour

class DataExportBase(BaseModel):
    export_type: str = Field(..., min_length=1, max_length=100)
    format: str = Field(..., max_length=20)
    filters: Dict[str, Any] = Field(default_factory=dict)
    fields: List[str] = Field(default_factory=list)
    date_range: Dict[str, Any] = Field(default_factory=dict)

# Create Models
class AnalyticsEventCreate(AnalyticsEventBase):
    session_id: Optional[str] = Field(None, max_length=255)

class PerformanceMetricCreate(PerformanceMetricBase):
    pass

class PredictiveModelCreate(PredictiveModelBase):
    pass

class ComparativeAnalysisCreate(ComparativeAnalysisBase):
    pass

class CustomReportCreate(CustomReportBase):
    pass

class AnalyticsDashboardCreate(AnalyticsDashboardBase):
    pass

class DataExportCreate(DataExportBase):
    pass

# Update Models
class AnalyticsEventUpdate(BaseModel):
    event_data: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = Field(None, ge=0)

class PerformanceMetricUpdate(BaseModel):
    metric_value: Optional[float] = None
    metric_unit: Optional[str] = Field(None, max_length=50)
    metadata: Optional[Dict[str, Any]] = None

class PredictiveModelUpdate(BaseModel):
    actual_value: Optional[float] = None
    accuracy_score: Optional[float] = Field(None, ge=0.0, le=1.0)

class ComparativeAnalysisUpdate(BaseModel):
    comparison_data: Optional[Dict[str, Any]] = None

class CustomReportUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    metrics: Optional[List[str]] = None
    visualizations: Optional[List[Dict[str, Any]]] = None
    is_scheduled: Optional[bool] = None
    schedule_frequency: Optional[str] = Field(None, max_length=50)
    export_format: Optional[str] = Field(None, max_length=20)
    email_recipients: Optional[List[str]] = None
    is_active: Optional[bool] = None

class AnalyticsDashboardUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    layout_config: Optional[Dict[str, Any]] = None
    widget_configs: Optional[List[Dict[str, Any]]] = None
    default_filters: Optional[Dict[str, Any]] = None
    refresh_interval: Optional[int] = Field(None, ge=30, le=3600)
    is_active: Optional[bool] = None

# Response Models
class AnalyticsEventResponse(AnalyticsEventBase):
    id: str
    user_id: Optional[str]
    session_id: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True

class PerformanceMetricResponse(PerformanceMetricBase):
    id: str
    user_id: str
    recorded_at: datetime
    
    class Config:
        from_attributes = True

class PredictiveModelResponse(PredictiveModelBase):
    id: str
    user_id: str
    predicted_at: datetime
    actual_value: Optional[float]
    validated_at: Optional[datetime]
    accuracy_score: Optional[float]
    
    class Config:
        from_attributes = True

class ComparativeAnalysisResponse(ComparativeAnalysisBase):
    id: str
    user_id: str
    analyzed_at: datetime
    
    class Config:
        from_attributes = True

class CustomReportResponse(CustomReportBase):
    id: str
    user_id: str
    last_generated: Optional[datetime]
    next_generation: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ReportExecutionResponse(BaseModel):
    id: str
    custom_report_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    data_points: int
    file_size_bytes: Optional[int]
    file_url: Optional[str]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True

class AnalyticsDashboardResponse(AnalyticsDashboardBase):
    id: str
    user_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DataExportResponse(DataExportBase):
    id: str
    user_id: str
    status: str
    progress_percentage: float
    file_size_bytes: Optional[int]
    file_url: Optional[str]
    download_count: int
    error_message: Optional[str]
    requested_at: datetime
    completed_at: Optional[datetime]
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Search/Filter Models
class AnalyticsEventSearchParams(BaseModel):
    event_type: Optional[AnalyticsEventType] = None
    event_name: Optional[str] = None
    page_url: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)

class PerformanceMetricSearchParams(BaseModel):
    metric_name: Optional[str] = None
    module_type: Optional[str] = None
    skill_area: Optional[str] = None
    difficulty_level: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)

class PredictiveModelSearchParams(BaseModel):
    model_type: Optional[str] = None
    model_version: Optional[str] = None
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_validated: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)

class CustomReportSearchParams(BaseModel):
    report_type: Optional[ReportType] = None
    is_scheduled: Optional[bool] = None
    is_active: Optional[bool] = None
    name: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

class DataExportSearchParams(BaseModel):
    export_type: Optional[str] = None
    format: Optional[str] = None
    status: Optional[str] = None
    requested_after: Optional[datetime] = None
    requested_before: Optional[datetime] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

# Analytics Dashboard Models
class DashboardWidget(BaseModel):
    id: str
    type: str
    title: str
    config: Dict[str, Any]
    data: Optional[Dict[str, Any]] = None

class DashboardLayout(BaseModel):
    widgets: List[DashboardWidget]
    layout: Dict[str, Any]

class AnalyticsSummary(BaseModel):
    total_events: int
    total_metrics: int
    total_predictions: int
    total_reports: int
    total_exports: int
    recent_activity: List[Dict[str, Any]]

# Advanced Analytics Models
class TrendAnalysis(BaseModel):
    metric_name: str
    trend_direction: str  # increasing, decreasing, stable
    change_percentage: float
    time_period: str
    data_points: List[Dict[str, Any]]

class CorrelationAnalysis(BaseModel):
    variable1: str
    variable2: str
    correlation_coefficient: float
    significance_level: float
    sample_size: int
    interpretation: str

class AnomalyDetection(BaseModel):
    metric_name: str
    detected_anomalies: List[Dict[str, Any]]
    threshold_value: float
    confidence_level: float

class PredictiveInsight(BaseModel):
    insight_type: str
    title: str
    description: str
    confidence_score: float
    predicted_value: float
    target_date: datetime
    factors: List[str]
    recommendations: List[str]

class ComparativeInsight(BaseModel):
    comparison_type: str
    user_performance: float
    peer_average: float
    percentile_rank: float
    improvement_potential: float
    recommendations: List[str]

# Report Generation Models
class ReportTemplate(BaseModel):
    id: str
    name: str
    description: str
    template_type: ReportType
    sections: List[Dict[str, Any]]
    default_config: Dict[str, Any]

class ReportGenerationRequest(BaseModel):
    report_type: ReportType
    template_id: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    format: str = "pdf"
    include_charts: bool = True
    include_data_tables: bool = True

class ReportGenerationResponse(BaseModel):
    report_id: str
    status: str
    estimated_completion_time: Optional[int] = None
    download_url: Optional[str] = None
    file_size: Optional[int] = None

# Data Export Models
class ExportConfiguration(BaseModel):
    export_type: str
    format: str
    fields: List[str]
    filters: Dict[str, Any]
    date_range: Dict[str, Any]
    include_metadata: bool = True
    compression: bool = False

class ExportStatus(BaseModel):
    export_id: str
    status: str
    progress_percentage: float
    estimated_completion_time: Optional[int] = None
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None

# Validation Models
class AnalyticsValidation(BaseModel):
    data_quality_score: float
    completeness_score: float
    accuracy_score: float
    consistency_score: float
    issues: List[Dict[str, Any]]
    recommendations: List[str]

# Real-time Analytics Models
class RealTimeMetric(BaseModel):
    metric_name: str
    current_value: float
    previous_value: float
    change_percentage: float
    trend: str
    last_updated: datetime

class RealTimeDashboard(BaseModel):
    user_id: str
    metrics: List[RealTimeMetric]
    alerts: List[Dict[str, Any]]
    last_refresh: datetime
