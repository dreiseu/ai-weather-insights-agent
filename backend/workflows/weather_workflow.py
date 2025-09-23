import asyncio
from typing import Dict, Any, Optional, TypedDict, List
from datetime import datetime, timezone, timedelta
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from agents.data_agent import DataAgent, WeatherAnalysis
from agents.forecast_agent import ForecastAgent, ForecastAnalysis
from agents.advice_agent import AdviceAgent, AdviceReport
from services.weather_api import OpenWeatherService, WeatherData, ForecastData
from services.rag_service import RAGService, RAGResult

# Setup timezone (GMT+8 for Philippines)
PHILIPPINE_TZ = timezone(timedelta(hours=8))


class WorkflowState(TypedDict):
    """State passed between workflow nodes"""
    location: str
    latitude: Optional[float]
    longitude: Optional[float]
    current_weather: Optional[WeatherData]
    forecast_data: Optional[ForecastData]
    data_analysis: Optional[WeatherAnalysis]
    forecast_analysis: Optional[ForecastAnalysis]
    advice_report: Optional[AdviceReport]
    rag_knowledge: Optional[List[RAGResult]]
    error: Optional[str]
    audience: str  # farmers, officials, general_public


class WeatherInsightsResult(BaseModel):
    """Final result from weather insights workflow"""
    location: str
    analysis_time: datetime
    data_quality: WeatherAnalysis
    forecast_insights: ForecastAnalysis
    recommendations: AdviceReport
    relevant_knowledge: List[RAGResult]
    success: bool
    error_message: Optional[str] = None


class WeatherInsightsWorkflow:
    """LangGraph workflow coordinating Data → Forecast → Advice agents"""
    
    def __init__(
        self,
        openai_api_key: str,
        openweather_api_key: str,
        qdrant_url: str = "http://localhost:6333"
    ):
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=openai_api_key,
            temperature=0.3  # Slightly creative but focused
        )
        
        # Initialize services
        self.weather_service = OpenWeatherService(openweather_api_key)
        self.rag_service = RAGService(qdrant_url)
        
        # Initialize agents
        self.data_agent = DataAgent(self.llm)
        self.forecast_agent = ForecastAgent(self.llm)
        self.advice_agent = AdviceAgent(self.llm)
        
        # Build workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create workflow graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("fetch_weather", self._fetch_weather_data)
        workflow.add_node("analyze_data", self._analyze_data_quality)
        workflow.add_node("forecast_analysis", self._analyze_forecast)
        workflow.add_node("retrieve_knowledge", self._retrieve_relevant_knowledge)
        workflow.add_node("generate_advice", self._generate_recommendations)
        
        # Define workflow edges
        workflow.set_entry_point("fetch_weather")
        workflow.add_edge("fetch_weather", "analyze_data")
        workflow.add_edge("analyze_data", "forecast_analysis")
        workflow.add_edge("forecast_analysis", "retrieve_knowledge")
        workflow.add_edge("retrieve_knowledge", "generate_advice")
        workflow.add_edge("generate_advice", END)
        
        return workflow.compile()
    
    async def _fetch_weather_data(self, state: WorkflowState) -> WorkflowState:
        """Node 1: Fetch current weather and forecast data"""
        try:
            location = state["location"]
            
            # Get coordinates if not provided
            if not state.get("latitude") or not state.get("longitude"):
                lat, lon = await self.weather_service.get_coordinates(location)
                state["latitude"] = lat
                state["longitude"] = lon
            else:
                lat, lon = state["latitude"], state["longitude"]
            
            # Fetch current weather and forecast in parallel
            current_weather_task = self.weather_service.get_current_weather(lat, lon, location)
            forecast_task = self.weather_service.get_forecast(lat, lon, location)
            
            current_weather, forecast_data = await asyncio.gather(
                current_weather_task,
                forecast_task
            )
            
            state["current_weather"] = current_weather
            state["forecast_data"] = forecast_data
            
        except Exception as e:
            state["error"] = f"Weather data fetch failed: {str(e)}"
        
        return state
    
    async def _analyze_data_quality(self, state: WorkflowState) -> WorkflowState:
        """Node 2: Analyze weather data quality using Data Agent"""
        try:
            current_weather = state.get("current_weather")
            forecast_data = state.get("forecast_data")
            
            if not current_weather or not forecast_data:
                state["error"] = "Missing weather data for analysis"
                return state
            
            # Analyze current weather data quality
            data_analysis = await self.data_agent.process_weather_data(current_weather)
            state["data_analysis"] = data_analysis
            
        except Exception as e:
            state["error"] = f"Data analysis failed: {str(e)}"
        
        return state
    
    async def _analyze_forecast(self, state: WorkflowState) -> WorkflowState:
        """Node 3: Analyze forecast and predict implications using Forecast Agent"""
        try:
            current_weather = state.get("current_weather")
            forecast_data = state.get("forecast_data")
            
            if not current_weather or not forecast_data:
                state["error"] = "Missing weather data for forecast analysis"
                return state
            
            # Generate forecast insights
            audience = state.get("audience", "general")
            forecast_analysis = await self.forecast_agent.analyze_forecast(
                current_weather, 
                forecast_data,
                audience
            )
            state["forecast_analysis"] = forecast_analysis
            
        except Exception as e:
            state["error"] = f"Forecast analysis failed: {str(e)}"
        
        return state
    
    async def _retrieve_relevant_knowledge(self, state: WorkflowState) -> WorkflowState:
        """Node 4: Retrieve relevant knowledge from RAG system"""
        try:
            current_weather = state.get("current_weather")
            forecast_analysis = state.get("forecast_analysis")
            audience = state.get("audience", "general")
            
            if not current_weather or not forecast_analysis:
                state["error"] = "Missing data for knowledge retrieval"
                return state
            
            # Create search query from weather conditions and insights
            weather_conditions = f"{current_weather.weather_condition} {current_weather.description}"
            
            # Add forecast insights to search context
            if forecast_analysis.risk_alerts:
                weather_conditions += " " + " ".join(forecast_analysis.risk_alerts)
            
            # Retrieve contextual knowledge
            relevant_knowledge = await self.rag_service.get_contextual_knowledge(
                weather_condition=weather_conditions,
                location=current_weather.location,
                audience=audience
            )
            
            state["rag_knowledge"] = relevant_knowledge
            
        except Exception as e:
            state["error"] = f"Knowledge retrieval failed: {str(e)}"
        
        return state
    
    async def _generate_recommendations(self, state: WorkflowState) -> WorkflowState:
        """Node 5: Generate actionable advice using Advice Agent"""
        try:
            data_analysis = state.get("data_analysis")
            forecast_analysis = state.get("forecast_analysis")
            
            if not data_analysis or not forecast_analysis:
                state["error"] = "Missing analysis data for advice generation"
                return state
            
            # Generate comprehensive advice
            audience = state.get("audience", "general")
            advice_report = await self.advice_agent.generate_advice(
                data_analysis,
                forecast_analysis,
                audience
            )
            
            state["advice_report"] = advice_report
            
        except Exception as e:
            state["error"] = f"Advice generation failed: {str(e)}"
        
        return state
    
    async def run_analysis(
        self,
        location: str,
        audience: str = "general",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> WeatherInsightsResult:
        """Run complete weather insights analysis workflow"""
        
        # Initialize workflow state
        initial_state: WorkflowState = {
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": None,
            "forecast_data": None,
            "data_analysis": None,
            "forecast_analysis": None,
            "advice_report": None,
            "rag_knowledge": None,
            "error": None,
            "audience": audience
        }
        
        # Execute workflow
        final_state = await self.workflow.ainvoke(initial_state)
        
        # Check for errors
        if final_state.get("error"):
            return WeatherInsightsResult(
                location=location,
                analysis_time=datetime.now(PHILIPPINE_TZ),
                data_quality=None,
                forecast_insights=None,
                recommendations=None,
                relevant_knowledge=[],
                success=False,
                error_message=final_state["error"]
            )
        
        # Compile successful result
        return WeatherInsightsResult(
            location=location,
            analysis_time=datetime.now(PHILIPPINE_TZ),
            data_quality=final_state["data_analysis"],
            forecast_insights=final_state["forecast_analysis"],
            recommendations=final_state["advice_report"],
            relevant_knowledge=final_state.get("rag_knowledge", []),
            success=True
        )
    
    async def run_batch_analysis(
        self,
        locations: List[str],
        audience: str = "general"
    ) -> List[WeatherInsightsResult]:
        """Run analysis for multiple locations in parallel"""
        
        tasks = [
            self.run_analysis(location, audience)
            for location in locations
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(
                    WeatherInsightsResult(
                        location=locations[i],
                        analysis_time=datetime.now(PHILIPPINE_TZ),
                        data_quality=None,
                        forecast_insights=None,
                        recommendations=None,
                        relevant_knowledge=[],
                        success=False,
                        error_message=str(result)
                    )
                )
            else:
                final_results.append(result)
        
        return final_results
    
    async def get_workflow_status(self) -> Dict[str, Any]:
        """Get workflow system status"""
        try:
            # Test weather service
            weather_status = "operational"
            try:
                await self.weather_service.get_coordinates("Manila")
            except:
                weather_status = "error"
            
            # Test RAG service
            rag_status = "operational"
            rag_stats = {}
            try:
                rag_stats = await self.rag_service.get_collection_stats()
            except:
                rag_status = "error"
            
            return {
                "workflow": "operational",
                "weather_service": weather_status,
                "rag_service": rag_status,
                "rag_knowledge_base": rag_stats,
                "agents": {
                    "data_agent": "operational",
                    "forecast_agent": "operational", 
                    "advice_agent": "operational"
                },
                "timestamp": datetime.now(PHILIPPINE_TZ).isoformat()
            }
            
        except Exception as e:
            return {
                "workflow": "error",
                "error": str(e),
                "timestamp": datetime.now(PHILIPPINE_TZ).isoformat()
            }
    
    def close(self):
        """Clean up resources"""
        self.rag_service.close()