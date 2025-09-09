import asyncio
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pandas as pd
from pydantic import BaseModel


class WeatherData(BaseModel):
    """Structured weather data model"""
    location: str
    latitude: float
    longitude: float
    temperature: float
    humidity: int
    pressure: float
    wind_speed: float
    wind_direction: int
    weather_condition: str
    description: str
    timestamp: datetime
    visibility: Optional[float] = None
    uv_index: Optional[float] = None


class ForecastData(BaseModel):
    """5-day forecast data model"""
    location: str
    forecasts: List[WeatherData]


class OpenWeatherService:
    """OpenWeather API integration service"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.geocoding_url = "http://api.openweathermap.org/geo/1.0"
        
    async def get_coordinates(self, city_name: str, country_code: Optional[str] = None) -> tuple[float, float]:
        """Get latitude and longitude for a city"""
        query = f"{city_name}"
        if country_code:
            query += f",{country_code}"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.geocoding_url}/direct",
                params={
                    "q": query,
                    "limit": 1,
                    "appid": self.api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if not data:
                raise ValueError(f"City not found: {city_name}")
                
            return data[0]["lat"], data[0]["lon"]
    
    async def get_current_weather(self, lat: float, lon: float, location_name: str = None) -> WeatherData:
        """Fetch current weather data"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return self._parse_current_weather(data, location_name or f"{lat},{lon}")
    
    async def get_current_weather_by_city(self, city_name: str, country_code: Optional[str] = None) -> WeatherData:
        """Fetch current weather by city name"""
        lat, lon = await self.get_coordinates(city_name, country_code)
        return await self.get_current_weather(lat, lon, city_name)
    
    async def get_forecast(self, lat: float, lon: float, location_name: str = None) -> ForecastData:
        """Fetch 5-day weather forecast"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/forecast",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return self._parse_forecast(data, location_name or f"{lat},{lon}")
    
    async def get_forecast_by_city(self, city_name: str, country_code: Optional[str] = None) -> ForecastData:
        """Fetch 5-day forecast by city name"""
        lat, lon = await self.get_coordinates(city_name, country_code)
        return await self.get_forecast(lat, lon, city_name)
    
    def _parse_current_weather(self, data: Dict[str, Any], location: str) -> WeatherData:
        """Parse OpenWeather API response to WeatherData model"""
        main = data["main"]
        weather = data["weather"][0]
        wind = data.get("wind", {})
        
        return WeatherData(
            location=location,
            latitude=data["coord"]["lat"],
            longitude=data["coord"]["lon"],
            temperature=main["temp"],
            humidity=main["humidity"],
            pressure=main["pressure"],
            wind_speed=wind.get("speed", 0),
            wind_direction=wind.get("deg", 0),
            weather_condition=weather["main"],
            description=weather["description"],
            timestamp=datetime.fromtimestamp(data["dt"]),
            visibility=data.get("visibility", 0) / 1000 if data.get("visibility") else None,  # Convert to km
            uv_index=None  # Not available in current weather endpoint
        )
    
    def _parse_forecast(self, data: Dict[str, Any], location: str) -> ForecastData:
        """Parse forecast API response to ForecastData model"""
        forecasts = []
        city_data = data["city"]
        
        for item in data["list"]:
            main = item["main"]
            weather = item["weather"][0]
            wind = item.get("wind", {})
            
            forecast_item = WeatherData(
                location=location,
                latitude=city_data["coord"]["lat"],
                longitude=city_data["coord"]["lon"],
                temperature=main["temp"],
                humidity=main["humidity"],
                pressure=main["pressure"],
                wind_speed=wind.get("speed", 0),
                wind_direction=wind.get("deg", 0),
                weather_condition=weather["main"],
                description=weather["description"],
                timestamp=datetime.fromtimestamp(item["dt"]),
                visibility=item.get("visibility", 0) / 1000 if item.get("visibility") else None,
                uv_index=None
            )
            forecasts.append(forecast_item)
        
        return ForecastData(location=location, forecasts=forecasts)
    
    def weather_to_dataframe(self, weather_data: WeatherData) -> pd.DataFrame:
        """Convert WeatherData to pandas DataFrame for processing"""
        return pd.DataFrame([weather_data.dict()])
    
    def forecast_to_dataframe(self, forecast_data: ForecastData) -> pd.DataFrame:
        """Convert ForecastData to pandas DataFrame for processing"""
        return pd.DataFrame([forecast.dict() for forecast in forecast_data.forecasts])