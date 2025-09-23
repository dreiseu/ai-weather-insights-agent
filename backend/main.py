import asyncio
import time
from datetime import datetime, timezone, timedelta
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from pydantic_settings import BaseSettings

from workflows.weather_workflow import WeatherInsightsWorkflow, WeatherInsightsResult
from models.schemas import (
    WeatherRequest, BatchWeatherRequest,
    WeatherInsightsResponse, BatchWeatherInsightsResponse,
    SystemStatusResponse, HealthResponse, ErrorResponse,
    WeatherCondition, DataQualityResponse, ForecastResponse, 
    AdviceResponse, KnowledgeItem, ForecastInsight, Recommendation
)


class Settings(BaseSettings):
    """Application settings"""
    openai_api_key: str
    openweather_api_key: str
    qdrant_url: str = "http://localhost:6333"
    environment: str = "development"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"


# Global variables
settings = Settings()
workflow: WeatherInsightsWorkflow = None

# Setup timezone (GMT+8 for Philippines)
PHILIPPINE_TZ = timezone(timedelta(hours=8))
start_time = datetime.now(PHILIPPINE_TZ)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global workflow
    
    # Startup
    print("🌦️ Starting AI Weather Insights Agent...")
    workflow = WeatherInsightsWorkflow(
        openai_api_key=settings.openai_api_key,
        openweather_api_key=settings.openweather_api_key,
        qdrant_url=settings.qdrant_url
    )
    print("✅ Weather Insights Agent ready!")
    
    yield
    
    # Shutdown
    print("🔄 Shutting down Weather Insights Agent...")
    if workflow:
        workflow.close()
    print("✅ Shutdown complete!")


# Create FastAPI app
app = FastAPI(
    title="AI Weather Insights Agent",
    description="Transforms raw weather data into actionable insights for rural communities, farmers, and local officials",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper functions
def convert_workflow_result_to_response(result: WeatherInsightsResult) -> WeatherInsightsResponse:
    """Convert workflow result to API response format"""
    
    if not result.success:
        return WeatherInsightsResponse(
            location=result.location,
            analysis_time=result.analysis_time,
            current_weather=None,
            data_quality=None,
            forecast_insights=None,
            recommendations=None,
            relevant_knowledge=[],
            success=False,
            error_message=result.error_message
        )
    
    # Convert current weather
    current_weather_data = None
    if hasattr(result.data_quality, 'cleaned_data') and result.data_quality.cleaned_data:
        weather_dict = result.data_quality.cleaned_data
        if isinstance(weather_dict, list):
            weather_dict = weather_dict[0] if weather_dict else {}
        
        current_weather_data = WeatherCondition(
            location=weather_dict.get('location', result.location),
            temperature=weather_dict.get('temperature', 0),
            humidity=weather_dict.get('humidity', 0),
            pressure=weather_dict.get('pressure', 0),
            wind_speed=weather_dict.get('wind_speed', 0),
            weather_condition=weather_dict.get('weather_condition', 'Unknown'),
            description=weather_dict.get('description', ''),
            timestamp=weather_dict.get('timestamp') if isinstance(weather_dict.get('timestamp'), datetime) else datetime.fromisoformat(weather_dict.get('timestamp', datetime.now().isoformat()))
        )
    
    # Convert data quality
    data_quality = DataQualityResponse(
        quality_score=result.data_quality.quality_score,
        anomalies_detected=result.data_quality.anomalies_detected,
        summary=result.data_quality.summary,
        recommendations=result.data_quality.recommendations
    )
    
    # Convert forecast insights
    forecast_insights = ForecastResponse(
        location=result.forecast_insights.location,
        insights=[
            ForecastInsight(
                category=insight.category,
                priority=insight.priority,
                time_horizon=insight.time_horizon,
                title=insight.title,
                description=insight.description,
                confidence=insight.confidence
            ) for insight in result.forecast_insights.insights
        ],
        weather_trends=result.forecast_insights.weather_trends,
        risk_alerts=result.forecast_insights.risk_alerts,
        analysis_time=result.forecast_insights.analysis_time
    )
    
    # Convert recommendations
    recommendations = AdviceResponse(
        location=result.recommendations.location,
        recommendations=[
            Recommendation(
                target_audience=rec.target_audience,
                action_type=rec.action_type,
                priority=rec.priority,
                title=rec.title,
                action=rec.action,
                reasoning=rec.reasoning,
                timing=rec.timing,
                resources_needed=rec.resources_needed
            ) for rec in result.recommendations.recommendations
        ],
        priority_summary=result.recommendations.priority_summary,
        action_checklist=result.recommendations.action_checklist,
        contact_suggestions=result.recommendations.contact_suggestions,
        report_time=result.recommendations.report_time
    )
    
    # Convert knowledge items
    knowledge_items = [
        KnowledgeItem(
            content=item.content,
            score=item.score,
            source=item.source,
            category=item.category,
            location=item.location
        ) for item in result.relevant_knowledge
    ]
    
    return WeatherInsightsResponse(
        location=result.location,
        analysis_time=result.analysis_time,
        current_weather=current_weather_data,
        data_quality=data_quality,
        forecast_insights=forecast_insights,
        recommendations=recommendations,
        relevant_knowledge=knowledge_items,
        success=True
    )


# API Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with basic service info"""
    uptime = datetime.now(PHILIPPINE_TZ) - start_time
    return HealthResponse(
        status="operational",
        uptime=str(uptime).split('.')[0]  # Remove microseconds
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = datetime.now(PHILIPPINE_TZ) - start_time
    return HealthResponse(
        status="operational",
        uptime=str(uptime).split('.')[0]
    )

@app.post("/api/test-connection")
async def test_connection(data: dict):
    """Simple test endpoint to verify frontend-backend connection"""
    return {
        "status": "success",
        "message": "Backend received your request successfully!",
        "received_data": data,
        "timestamp": datetime.now(PHILIPPINE_TZ).isoformat()
    }


@app.post("/api/weather/insights", response_model=WeatherInsightsResponse)
async def get_weather_insights(request: WeatherRequest):
    """Get comprehensive weather insights for a single location"""
    try:
        print(f"🔍 Starting analysis for {request.location}, audience: {request.audience}")
        start_analysis = time.time()
        
        print(f"🔍 Calling workflow.run_analysis...")
        result = await workflow.run_analysis(
            location=request.location,
            audience=request.audience,
            latitude=request.latitude,
            longitude=request.longitude
        )
        
        print(f"🔍 Converting workflow result to response...")
        response = convert_workflow_result_to_response(result)
        
        # Log processing time
        processing_time = time.time() - start_analysis
        print(f"✅ Analysis completed for {request.location} in {processing_time:.2f}s")
        
        return response
        
    except Exception as e:
        print(f"❌ DETAILED ERROR for {request.location}:")
        print(f"❌ Error type: {type(e).__name__}")
        print(f"❌ Error message: {str(e)}")
        import traceback
        print(f"❌ Full traceback:")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/api/weather/batch", response_model=BatchWeatherInsightsResponse)
async def get_batch_weather_insights(request: BatchWeatherRequest):
    """Get weather insights for multiple locations"""
    try:
        start_batch = time.time()
        
        results = await workflow.run_batch_analysis(
            locations=request.locations,
            audience=request.audience
        )
        
        # Convert results to response format
        responses = [convert_workflow_result_to_response(result) for result in results]
        
        # Calculate statistics
        successful = sum(1 for r in responses if r.success)
        failed = len(responses) - successful
        processing_time = time.time() - start_batch
        
        print(f"✅ Batch analysis completed: {successful}/{len(request.locations)} successful in {processing_time:.2f}s")
        
        return BatchWeatherInsightsResponse(
            results=responses,
            total_locations=len(request.locations),
            successful_analyses=successful,
            failed_analyses=failed,
            processing_time=processing_time
        )
        
    except Exception as e:
        print(f"❌ Error processing batch request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch analysis failed: {str(e)}"
        )


@app.get("/api/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get system status and health information"""
    try:
        status_info = await workflow.get_workflow_status()
        
        services = []
        for service_name, service_status in status_info.items():
            if service_name not in ['timestamp', 'rag_knowledge_base']:
                services.append({
                    "name": service_name,
                    "status": service_status if isinstance(service_status, str) else "operational",
                    "details": service_status if isinstance(service_status, dict) else None
                })
        
        return SystemStatusResponse(
            workflow=status_info.get("workflow", "unknown"),
            services=services,
            knowledge_base_stats=status_info.get("rag_knowledge_base", {}),
            timestamp=datetime.fromisoformat(status_info.get("timestamp", datetime.now().isoformat()))
        )
        
    except Exception as e:
        print(f"❌ Error getting system status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Status check failed: {str(e)}"
        )


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_type="HTTP_ERROR",
            message=str(exc.detail),
            details={"status_code": exc.status_code}
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    print(f"❌ Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_type="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            details={"exception": str(exc)}
        ).dict()
    )


if __name__ == "__main__":
    print("🚀 Starting AI Weather Insights Agent API...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )