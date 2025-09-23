import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta, timezone
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from services.weather_api import WeatherData, ForecastData

# Setup timezone (GMT+8 for Philippines)
PHILIPPINE_TZ = timezone(timedelta(hours=8))


class WeatherInsight(BaseModel):
    """Individual weather insight or prediction"""
    category: str = Field(description="Type of insight: agriculture, disaster, general")
    priority: str = Field(description="Priority level: low, medium, high, critical")
    time_horizon: str = Field(description="Time frame: immediate, 24h, 3-day, weekly")
    title: str = Field(description="Brief insight title")
    description: str = Field(description="Detailed explanation")
    confidence: float = Field(ge=0, le=1, description="Confidence in prediction")


class ForecastAnalysis(BaseModel):
    """Complete forecast analysis result"""
    location: str
    analysis_time: datetime
    insights: List[WeatherInsight]
    weather_trends: List[str] = Field(default_factory=list)
    risk_alerts: List[str] = Field(default_factory=list)
    summary: str


class ForecastAgent:
    """AI agent that analyzes weather forecasts and predicts implications"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self._audience_prompt_cache = {}  # Cache for generated prompts
        
        self.prompt = ChatPromptTemplate.from_template("""
        You are a weather forecasting specialist helping rural communities and farmers.
        
        Analyze this weather forecast data and provide practical insights:
        
        Current Weather:
        {current_weather}
        
        5-Day Forecast:
        {forecast_data}
        
        Your task is to:
        1. Identify weather patterns and trends
        2. Predict implications for farming, fishing, and daily activities
        3. Assess disaster risks (flooding, drought, storms)
        4. Provide timing for optimal activities
        5. Rate confidence in predictions
        
        Focus on:
        - Agricultural impact (planting, harvesting, irrigation)
        - Disaster preparedness needs
        - Daily activity planning
        - Economic implications for rural livelihoods
        
        Provide insights in this format:
        WEATHER TRENDS: [major patterns you observe]
        
        AGRICULTURE INSIGHTS:
        - [specific farming recommendations with timing]
        
        DISASTER RISKS:
        - [potential hazards and preparation needed]
        
        TIMING RECOMMENDATIONS:
        - [best times for outdoor work, travel, etc.]
        
        CONFIDENCE LEVEL: [high/medium/low] - [brief reasoning]
        
        Use simple language that non-experts can understand.
        """)
    
    async def analyze_forecast(
        self, 
        current_weather: WeatherData,
        forecast_data: ForecastData,
        audience: str = "general"
    ) -> ForecastAnalysis:
        """Analyze weather forecast and generate insights"""
        
        # Prepare data summaries for AI analysis
        current_summary = self._summarize_current_conditions(current_weather)
        forecast_summary = self._summarize_forecast_patterns(forecast_data)
        
        # Create audience-specific prompt
        audience_prompt = await self._create_audience_prompt(audience)
        
        # Get AI analysis
        messages = audience_prompt.format_messages(
            current_weather=current_summary,
            forecast_data=forecast_summary
        )
        response = await self.llm.ainvoke(messages)
        
        # Debug: Print the AI response to see what format it's using
        print(f"🔍 AI Forecast Response for {audience}:")
        print(f"--- START RESPONSE ---")
        print(response.content)
        print(f"--- END RESPONSE ---")
        
        # Generate structured insights using more robust parsing
        insights = await self._extract_insights_with_ai(response.content, forecast_data.location, audience)
        trends = self._identify_trends(forecast_data)
        risks = self._assess_risks(current_weather, forecast_data)
        
        return ForecastAnalysis(
            location=forecast_data.location,
            analysis_time=datetime.now(PHILIPPINE_TZ),
            insights=insights,
            weather_trends=trends,
            risk_alerts=risks,
            summary=response.content
        )
    
    async def _create_audience_prompt(self, audience: str) -> ChatPromptTemplate:
        """Create AI-generated audience-specific prompt for weather analysis"""
        
        # Check cache first to avoid regenerating the same prompt
        if audience in self._audience_prompt_cache:
            print(f"🔄 Using cached prompt for audience: {audience}")
            return self._audience_prompt_cache[audience]
        
        print(f"🤖 Generating AI-powered prompt for audience: {audience}")
        
        # Use AI to generate audience-specific prompt structure
        prompt_generator = ChatPromptTemplate.from_template("""
        You are an expert in creating specialized weather analysis prompts for different audiences.
        
        Create a comprehensive weather analysis prompt specifically tailored for: {audience}
        
        Your task is to design a prompt that will guide a weather analyst to provide the most relevant and actionable insights for this specific audience.
        
        Consider:
        1. What are the main concerns and priorities of {audience}?
        2. What weather-related decisions do they need to make?
        3. What terminology and language style is most appropriate?
        4. What specific weather impacts matter most to them?
        5. What format would be most useful for their decision-making?
        
        Generate a detailed prompt that includes:
        - Specific focus areas relevant to {audience}
        - Key activities/operations they need to consider
        - Risk factors they should be aware of
        - Decision-making timeframes important to them
        - Recommended output format structure
        - Appropriate language tone and complexity level
        
        Return ONLY the weather analysis prompt (not meta-commentary). The prompt should start with:
        "You are a weather forecasting specialist helping [audience]..."
        
        The prompt should include placeholders for {{current_weather}} and {{forecast_data}} that will be filled with actual weather information.
        
        Make sure the prompt is comprehensive, specific to the audience, and will generate highly relevant weather insights.
        """)
        
        # Generate the audience-specific prompt
        messages = prompt_generator.format_messages(audience=audience)
        response = await self.llm.ainvoke(messages)
        
        # Extract the generated prompt text
        generated_prompt = response.content.strip()
        
        # Create the ChatPromptTemplate and cache it
        audience_prompt = ChatPromptTemplate.from_template(generated_prompt)
        self._audience_prompt_cache[audience] = audience_prompt
        
        print(f"✅ Generated and cached prompt for audience: {audience}")
        return audience_prompt
    
    def _summarize_current_conditions(self, weather: WeatherData) -> str:
        """Summarize current weather conditions"""
        return f"""
        Temperature: {weather.temperature}°C (feels like weather condition)
        Humidity: {weather.humidity}%
        Pressure: {weather.pressure} hPa
        Wind: {weather.wind_speed} m/s from {weather.wind_direction}°
        Conditions: {weather.description}
        Time: {weather.timestamp.strftime('%Y-%m-%d %H:%M')}
        """
    
    def _summarize_forecast_patterns(self, forecast: ForecastData) -> str:
        """Summarize forecast patterns and trends"""
        df = pd.DataFrame([f.dict() for f in forecast.forecasts])
        
        # Temperature trends
        temp_trend = "stable"
        temp_diff = df['temperature'].iloc[-1] - df['temperature'].iloc[0]
        if temp_diff > 3:
            temp_trend = "warming"
        elif temp_diff < -3:
            temp_trend = "cooling"
        
        # Precipitation analysis
        rain_conditions = df[df['weather_condition'].isin(['Rain', 'Drizzle', 'Thunderstorm'])]
        rain_periods = len(rain_conditions)
        
        # Humidity patterns
        avg_humidity = df['humidity'].mean()
        humidity_trend = "normal"
        if avg_humidity > 80:
            humidity_trend = "high"
        elif avg_humidity < 40:
            humidity_trend = "low"
        
        # Wind analysis
        max_wind = df['wind_speed'].max()
        avg_wind = df['wind_speed'].mean()
        
        return f"""
        Forecast Period: {len(forecast.forecasts)} data points over 5 days
        Temperature Trend: {temp_trend} (from {df['temperature'].iloc[0]:.1f}°C to {df['temperature'].iloc[-1]:.1f}°C)
        Precipitation: {rain_periods} periods of rain/storms expected
        Humidity: {humidity_trend} ({avg_humidity:.0f}% average)
        Wind: Average {avg_wind:.1f} m/s, maximum {max_wind:.1f} m/s
        
        Daily Breakdown:
        {self._create_daily_summary(df)}
        """
    
    def _create_daily_summary(self, df: pd.DataFrame) -> str:
        """Create day-by-day forecast summary"""
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily_summary = []
        
        for date, day_data in df.groupby('date'):
            temp_range = f"{day_data['temperature'].min():.1f}-{day_data['temperature'].max():.1f}°C"
            conditions = day_data['weather_condition'].mode().iloc[0] if not day_data['weather_condition'].empty else "Unknown"
            avg_humidity = day_data['humidity'].mean()
            max_wind = day_data['wind_speed'].max()
            
            daily_summary.append(
                f"{date}: {temp_range}, {conditions}, {avg_humidity:.0f}% humidity, {max_wind:.1f} m/s wind"
            )
        
        return "\n".join(daily_summary[:5])  # Limit to 5 days
    
    def _identify_trends(self, forecast: ForecastData) -> List[str]:
        """Identify key weather trends"""
        df = pd.DataFrame([f.dict() for f in forecast.forecasts])
        trends = []
        
        # Temperature trend
        temp_slope = np.polyfit(range(len(df)), df['temperature'], 1)[0]
        if temp_slope > 0.5:
            trends.append("Temperatures rising over the forecast period")
        elif temp_slope < -0.5:
            trends.append("Temperatures falling over the forecast period")
        else:
            trends.append("Stable temperature pattern expected")
        
        # Humidity trend
        if df['humidity'].mean() > 75:
            trends.append("High humidity levels - increased thunderstorm risk")
        
        # Pressure trend
        pressure_slope = np.polyfit(range(len(df)), df['pressure'], 1)[0]
        if pressure_slope < -0.5:
            trends.append("Falling atmospheric pressure - potential weather system approaching")
        elif pressure_slope > 0.5:
            trends.append("Rising atmospheric pressure - clearing weather expected")
        
        # Wind patterns
        if df['wind_speed'].max() > 15:
            trends.append("High wind speeds expected - potential for severe weather")
        
        return trends
    
    def _assess_risks(self, current: WeatherData, forecast: ForecastData) -> List[str]:
        """Assess weather-related risks"""
        risks = []
        df = pd.DataFrame([f.dict() for f in forecast.forecasts])
        
        # Heat risk
        if df['temperature'].max() > 35:
            risks.append("HEAT WARNING: Extreme temperatures expected - risk of heat stress")
        
        # Cold risk
        if df['temperature'].min() < 0:
            risks.append("FROST WARNING: Freezing temperatures expected - protect crops and livestock")
        
        # Storm risk
        storm_conditions = df[df['weather_condition'].isin(['Thunderstorm', 'Squall'])]
        if not storm_conditions.empty:
            risks.append("STORM ALERT: Thunderstorms predicted - secure outdoor equipment")
        
        # Wind risk
        if df['wind_speed'].max() > 20:
            risks.append("HIGH WIND WARNING: Strong winds expected - avoid tall structures")
        
        # Humidity risk
        if df['humidity'].mean() > 85:
            risks.append("HIGH HUMIDITY: Increased risk of plant diseases and heat stress")
        
        # Drought risk (low humidity + no rain)
        rain_forecast = df[df['weather_condition'].isin(['Rain', 'Drizzle', 'Thunderstorm'])]
        if rain_forecast.empty and df['humidity'].mean() < 50:
            risks.append("DRY CONDITIONS: No rain expected - monitor irrigation needs")
        
        return risks
    
    def _extract_insights(self, ai_response: str, location: str) -> List[WeatherInsight]:
        """Extract structured insights from AI response"""
        insights = []
        
        # Parse AI response sections
        sections = {
            'agriculture': [],
            'disaster': [],
            'timing': []
        }
        
        current_section = None
        for line in ai_response.split('\n'):
            line = line.strip()
            if 'AGRICULTURE INSIGHTS:' in line:
                current_section = 'agriculture'
            elif 'DISASTER RISKS:' in line:
                current_section = 'disaster'  
            elif 'TIMING RECOMMENDATIONS:' in line:
                current_section = 'timing'
            elif line.startswith('- ') and current_section:
                sections[current_section].append(line[2:])
        
        # Create structured insights
        for category, items in sections.items():
            for item in items:
                priority = self._determine_priority(item)
                confidence = self._estimate_confidence(item)
                time_horizon = self._determine_time_horizon(item)
                
                insight = WeatherInsight(
                    category=category,
                    priority=priority,
                    time_horizon=time_horizon,
                    title=item.split('.')[0] if '.' in item else item[:50] + "...",
                    description=item,
                    confidence=confidence
                )
                insights.append(insight)
        
        return insights
    
    async def _extract_insights_with_ai(self, ai_response: str, location: str, audience: str) -> List[WeatherInsight]:
        """Extract structured insights from AI response using AI parsing"""
        
        # Use AI to extract structured insights from the response
        extraction_prompt = ChatPromptTemplate.from_template("""
        You are an expert at extracting structured information from weather analysis text.
        
        Analyze the following weather analysis response and extract specific insights in JSON format:
        
        {ai_response}
        
        Extract insights and classify them into these categories:
        - agriculture: farming, crops, livestock, planting, harvesting insights
        - disaster: weather risks, warnings, hazards, emergency preparations
        - general: daily activities, travel, outdoor work recommendations
        
        For each insight, determine:
        - priority: critical, high, medium, low
        - time_horizon: immediate, 24h, 3-day, weekly  
        - confidence: 0.0 to 1.0 (how confident is this prediction)
        - title: brief 5-8 word summary
        - description: the full insight text
        
        Return ONLY a JSON array with this exact structure:
        [
          {{
            "category": "agriculture|disaster|general",
            "priority": "critical|high|medium|low", 
            "time_horizon": "immediate|24h|3-day|weekly",
            "title": "Brief insight title",
            "description": "Full description of the insight",
            "confidence": 0.8
          }}
        ]
        
        Extract at least 3-8 insights. Focus on actionable, specific recommendations relevant to {audience}.
        """)
        
        try:
            messages = extraction_prompt.format_messages(
                ai_response=ai_response,
                audience=audience
            )
            response = await self.llm.ainvoke(messages)
            
            # Parse JSON response
            import json
            insights_data = json.loads(response.content.strip())
            
            # Convert to WeatherInsight objects
            insights = []
            for item in insights_data:
                insight = WeatherInsight(
                    category=item.get('category', 'general'),
                    priority=item.get('priority', 'medium'),
                    time_horizon=item.get('time_horizon', '24h'),
                    title=item.get('title', 'Weather insight'),
                    description=item.get('description', ''),
                    confidence=float(item.get('confidence', 0.7))
                )
                insights.append(insight)
            
            return insights
            
        except Exception as e:
            print(f"🚨 AI extraction failed: {e}")
            # Fallback to original parsing method
            return self._extract_insights_fallback(ai_response)
    
    def _extract_insights_fallback(self, ai_response: str) -> List[WeatherInsight]:
        """Fallback method using original parsing logic"""
        return self._extract_insights(ai_response, "unknown")
    
    def _determine_priority(self, text: str) -> str:
        """Determine priority level from text content"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['critical', 'urgent', 'warning', 'danger']):
            return 'critical'
        elif any(word in text_lower for word in ['important', 'risk', 'alert', 'avoid']):
            return 'high'
        elif any(word in text_lower for word in ['consider', 'monitor', 'watch']):
            return 'medium'
        else:
            return 'low'
    
    def _estimate_confidence(self, text: str) -> float:
        """Estimate confidence level"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['likely', 'expected', 'will']):
            return 0.8
        elif any(word in text_lower for word in ['possible', 'may', 'might']):
            return 0.6
        else:
            return 0.7
    
    def _determine_time_horizon(self, text: str) -> str:
        """Determine time horizon from text"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['today', 'now', 'immediate']):
            return 'immediate'
        elif any(word in text_lower for word in ['tomorrow', '24 hour', 'next day']):
            return '24h'
        elif any(word in text_lower for word in ['3 day', 'this week']):
            return '3-day'
        else:
            return 'weekly'