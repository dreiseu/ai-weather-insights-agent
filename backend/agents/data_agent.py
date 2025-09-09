import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from services.weather_api import WeatherData, ForecastData


class WeatherAnalysis(BaseModel):
    """Analysis result from data processing"""
    cleaned_data: Dict[str, Any]
    quality_score: float = Field(ge=0, le=1, description="Data quality score from 0 to 1")
    anomalies_detected: List[str] = Field(default_factory=list)
    summary: str
    recommendations: List[str] = Field(default_factory=list)


class DataAgent:
    """AI agent for processing and analyzing weather data from OpenWeather API"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        
        self.prompt = ChatPromptTemplate.from_template("""
        You are a weather data processing specialist for rural communities and farmers. 
        
        Analyze this weather data and provide insights in simple, actionable language:
        
        Weather Data:
        {weather_data}
        
        Your task:
        1. Assess data quality and completeness
        2. Identify any concerning weather patterns 
        3. Note any missing or unusual readings
        4. Provide a quality score (0-1) and brief explanation
        
        Focus on practical insights that farmers and local officials can understand.
        Avoid technical jargon - use plain language.
        
        Respond in this format:
        QUALITY SCORE: [0.0-1.0]
        ISSUES FOUND: [list any problems or "None detected"]
        DATA SUMMARY: [brief description of the weather data]
        RECOMMENDATIONS: [practical suggestions for data usage]
        """)
    
    async def process_weather_data(
        self, 
        weather_data: Union[WeatherData, ForecastData, List[Dict], pd.DataFrame]
    ) -> WeatherAnalysis:
        """Process weather data from OpenWeather API"""
        
        # Convert input to standardized format
        if isinstance(weather_data, WeatherData):
            data_dict = weather_data.dict()
            data_summary = self._summarize_current_weather(weather_data)
        elif isinstance(weather_data, ForecastData):
            data_dict = [forecast.dict() for forecast in weather_data.forecasts]
            data_summary = self._summarize_forecast_data(weather_data)
        elif isinstance(weather_data, pd.DataFrame):
            data_dict = weather_data.to_dict('records')
            data_summary = f"DataFrame with {len(weather_data)} weather records"
        else:
            data_dict = weather_data
            data_summary = f"Raw weather data with {len(data_dict)} records"
        
        # Create human-readable summary for AI analysis
        formatted_data = f"""
        Data Type: {type(weather_data).__name__}
        Summary: {data_summary}
        Raw Data: {str(data_dict)[:1000]}...  # Truncate for API limits
        """
        
        # Get AI analysis
        messages = self.prompt.format_messages(weather_data=formatted_data)
        response = await self.llm.ainvoke(messages)
        
        # Parse AI response
        quality_score, anomalies, recommendations = self._parse_ai_response(response.content)
        
        # Perform basic data validation
        validation_results = self._validate_weather_data(data_dict)
        
        return WeatherAnalysis(
            cleaned_data=data_dict,
            quality_score=max(quality_score, validation_results['score']),  # Take higher score
            anomalies_detected=anomalies + validation_results['anomalies'],
            summary=response.content,
            recommendations=recommendations + validation_results['recommendations']
        )
    
    def _summarize_current_weather(self, weather: WeatherData) -> str:
        """Create human-readable summary of current weather"""
        return f"""
        Location: {weather.location}
        Temperature: {weather.temperature}°C ({weather.description})
        Humidity: {weather.humidity}%
        Wind: {weather.wind_speed} m/s
        Pressure: {weather.pressure} hPa
        Time: {weather.timestamp}
        """
    
    def _summarize_forecast_data(self, forecast: ForecastData) -> str:
        """Create human-readable summary of forecast data"""
        temps = [f.temperature for f in forecast.forecasts]
        conditions = [f.weather_condition for f in forecast.forecasts]
        
        return f"""
        Location: {forecast.location}
        Forecast Period: {len(forecast.forecasts)} time points
        Temperature Range: {min(temps):.1f}°C to {max(temps):.1f}°C
        Main Conditions: {', '.join(set(conditions))}
        Start Time: {forecast.forecasts[0].timestamp}
        End Time: {forecast.forecasts[-1].timestamp}
        """
    
    def _validate_weather_data(self, data_dict: Union[Dict, List[Dict]]) -> Dict[str, Any]:
        """Basic validation of weather data from OpenWeather API"""
        
        # Convert single dict to list for uniform processing
        if isinstance(data_dict, dict):
            data_dict = [data_dict]
        
        anomalies = []
        recommendations = []
        issues = 0
        total_checks = 0
        
        for record in data_dict:
            # Temperature validation
            if 'temperature' in record:
                temp = record['temperature']
                total_checks += 1
                if temp < -60 or temp > 60:  # Extreme temperature check
                    anomalies.append(f"Extreme temperature reading: {temp}°C")
                    issues += 1
            
            # Humidity validation  
            if 'humidity' in record:
                humidity = record['humidity']
                total_checks += 1
                if humidity < 0 or humidity > 100:
                    anomalies.append(f"Invalid humidity reading: {humidity}%")
                    issues += 1
            
            # Pressure validation
            if 'pressure' in record:
                pressure = record['pressure']
                total_checks += 1
                if pressure < 800 or pressure > 1200:  # Extreme pressure
                    anomalies.append(f"Unusual pressure reading: {pressure} hPa")
                    issues += 1
            
            # Wind speed validation
            if 'wind_speed' in record:
                wind = record['wind_speed']
                total_checks += 1
                if wind > 50:  # Hurricane-force winds
                    anomalies.append(f"Extreme wind speed: {wind} m/s")
                    issues += 1
        
        # Calculate quality score
        score = 1.0 - (issues / max(total_checks, 1))
        
        # Generate recommendations based on findings
        if not anomalies:
            recommendations.append("Weather data appears reliable for analysis")
        else:
            recommendations.append("Review flagged readings before making critical decisions")
            
        if len(data_dict) < 5:
            recommendations.append("Consider gathering more data points for better insights")
        
        return {
            'score': score,
            'anomalies': anomalies,
            'recommendations': recommendations
        }
    
    def _parse_ai_response(self, response: str) -> tuple[float, List[str], List[str]]:
        """Parse structured AI response"""
        quality_score = 0.8  # Default
        anomalies = []
        recommendations = []
        
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('QUALITY SCORE:'):
                try:
                    score_str = line.split(':')[1].strip()
                    quality_score = float(score_str)
                except:
                    quality_score = 0.8
            
            elif line.startswith('ISSUES FOUND:'):
                issues_str = line.split(':', 1)[1].strip()
                if issues_str.lower() != "none detected":
                    anomalies.extend([issues_str])
            
            elif line.startswith('RECOMMENDATIONS:'):
                rec_str = line.split(':', 1)[1].strip()
                recommendations.extend([rec_str])
        
        return quality_score, anomalies, recommendations