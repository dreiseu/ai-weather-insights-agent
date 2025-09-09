from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Request Models
class WeatherRequest(BaseModel):
    """Request for weather analysis"""
    location: str = Field(..., description="City name or location")
    audience: str = Field(default="general", description="Target audience: farmers, officials, general")
    latitude: Optional[float] = Field(None, description="Optional latitude coordinate")
    longitude: Optional[float] = Field(None, description="Optional longitude coordinate")


class BatchWeatherRequest(BaseModel):
    """Request for batch weather analysis"""
    locations: List[str] = Field(..., description="List of locations to analyze")
    audience: str = Field(default="general", description="Target audience for all locations")


# Response Models
class WeatherCondition(BaseModel):
    """Current weather condition"""
    location: str
    temperature: float
    humidity: int
    pressure: float
    wind_speed: float
    weather_condition: str
    description: str
    timestamp: datetime


class DataQualityResponse(BaseModel):
    """Data quality analysis response"""
    quality_score: float = Field(..., ge=0, le=1)
    anomalies_detected: List[str]
    summary: str
    recommendations: List[str]


class ForecastInsight(BaseModel):
    """Individual forecast insight"""
    category: str
    priority: str
    time_horizon: str
    title: str
    description: str
    confidence: float = Field(..., ge=0, le=1)


class ForecastResponse(BaseModel):
    """Forecast analysis response"""
    location: str
    insights: List[ForecastInsight]
    weather_trends: List[str]
    risk_alerts: List[str]
    analysis_time: datetime


class Recommendation(BaseModel):
    """Action recommendation"""
    target_audience: str
    action_type: str
    priority: str
    title: str
    action: str
    reasoning: str
    timing: str
    resources_needed: List[str]


class AdviceResponse(BaseModel):
    """Advice and recommendations response"""
    location: str
    recommendations: List[Recommendation]
    priority_summary: str
    action_checklist: List[str]
    contact_suggestions: List[str]
    report_time: datetime


class KnowledgeItem(BaseModel):
    """RAG knowledge item"""
    content: str
    score: float = Field(..., ge=0, le=1)
    source: str
    category: str
    location: Optional[str] = None


# Main Response Model
class WeatherInsightsResponse(BaseModel):
    """Complete weather insights response"""
    location: str
    analysis_time: datetime
    current_weather: WeatherCondition
    data_quality: DataQualityResponse
    forecast_insights: ForecastResponse
    recommendations: AdviceResponse
    relevant_knowledge: List[KnowledgeItem]
    success: bool
    error_message: Optional[str] = None


class BatchWeatherInsightsResponse(BaseModel):
    """Batch weather insights response"""
    results: List[WeatherInsightsResponse]
    total_locations: int
    successful_analyses: int
    failed_analyses: int
    processing_time: float


# System Status Models
class ServiceStatus(BaseModel):
    """Individual service status"""
    name: str
    status: str  # operational, degraded, error
    details: Optional[Dict[str, Any]] = None


class SystemStatusResponse(BaseModel):
    """Overall system status"""
    workflow: str
    services: List[ServiceStatus]
    knowledge_base_stats: Dict[str, Any]
    timestamp: datetime


# Error Response Model
class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error_type: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# Health Check Response
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)
    uptime: Optional[str] = None