import { weatherUtils } from '../services/weatherApi';
import {
  Thermometer,
  Droplets,
  Wind,
  Gauge,
  MapPin,
  Clock,
  Eye,
  CloudRain,
  Compass
} from 'lucide-react';

export default function WeatherCard({ weatherData }) {
  if (!weatherData) {
    return (
      <div className="card">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-3 bg-gray-200 rounded"></div>
            <div className="h-3 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  // Handle different data structures
  const location = weatherData.location || 'Unknown Location';
  const temperature = weatherData.current_weather?.temperature || weatherData.temperature || 0;
  const humidity = weatherData.current_weather?.humidity || weatherData.humidity || 0;
  const weather_condition = weatherData.current_weather?.condition || weatherData.condition || 'unknown';
  const description = weather_condition;
  const timestamp = weatherData.analysis_time || weatherData.timestamp;
  const pressure = weatherData.current_weather?.pressure || weatherData.pressure || null;
  const wind_speed = weatherData.current_weather?.wind_speed || weatherData.wind_speed || null;
  const feels_like = weatherData.current_weather?.feels_like || weatherData.feels_like || null;
  const wind_direction = weatherData.current_weather?.wind_direction || weatherData.wind_direction || null;
  const visibility = weatherData.current_weather?.visibility || weatherData.visibility || null;
  const rainfall_1h = weatherData.current_weather?.rainfall_1h || weatherData.rainfall_1h || null;
  const rainfall_3h = weatherData.current_weather?.rainfall_3h || weatherData.rainfall_3h || null;
  const cloudiness = weatherData.current_weather?.cloudiness || weatherData.cloudiness || null;

  const weatherIcon = weatherUtils.getWeatherIcon(weather_condition);
  const formattedDate = timestamp ? weatherUtils.formatDate(timestamp) : 'Now';
  const formattedTemp = weatherUtils.formatTemperature(temperature);

  return (
    <div className="card card-hover">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-2">
          <MapPin className="w-5 h-5 text-gray-500" />
          <h3 className="text-lg font-semibold text-gray-900">{location}</h3>
        </div>
        <div className="text-2xl">{weatherIcon}</div>
      </div>

      {/* Main Weather Info */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        {/* Temperature */}
        <div className="text-center">
          <div className="text-3xl font-bold text-weather-blue mb-1">
            {formattedTemp}
          </div>
          {feels_like && (
            <div className="text-xs text-gray-500">
              Feels like {weatherUtils.formatTemperature(feels_like)}
            </div>
          )}
          <div className="text-sm text-gray-500 capitalize mt-1">{description}</div>
        </div>

        {/* Weather Condition & Time */}
        <div className="text-center">
          <div className="text-lg font-semibold text-gray-700 mb-1">
            {weather_condition}
          </div>
          {cloudiness !== null && (
            <div className="text-xs text-gray-500">
              {cloudiness}% cloudy
            </div>
          )}
          <div className="flex items-center justify-center text-sm text-gray-500 mt-1">
            <Clock className="w-4 h-4 mr-1" />
            {formattedDate}
          </div>
        </div>
      </div>

      {/* Weather Details Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {/* Humidity */}
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <Droplets className="w-5 h-5 text-blue-500 mx-auto mb-1" />
          <div className="text-lg font-semibold text-gray-700">{humidity}%</div>
          <div className="text-xs text-gray-500">Humidity</div>
        </div>

        {/* Wind Speed */}
        {wind_speed && (
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <Wind className="w-5 h-5 text-green-500 mx-auto mb-1" />
            <div className="text-lg font-semibold text-gray-700">
              {Math.round(wind_speed)} m/s
            </div>
            <div className="text-xs text-gray-500">Wind Speed</div>
          </div>
        )}

        {/* Wind Direction */}
        {wind_direction && (
          <div className="text-center p-3 bg-cyan-50 rounded-lg">
            <Compass className="w-5 h-5 text-cyan-500 mx-auto mb-1" />
            <div className="text-lg font-semibold text-gray-700">
              {wind_direction}°
            </div>
            <div className="text-xs text-gray-500">Wind Dir</div>
          </div>
        )}

        {/* Pressure */}
        {pressure && (
          <div className="text-center p-3 bg-purple-50 rounded-lg">
            <Gauge className="w-5 h-5 text-purple-500 mx-auto mb-1" />
            <div className="text-lg font-semibold text-gray-700">
              {Math.round(pressure)} hPa
            </div>
            <div className="text-xs text-gray-500">Pressure</div>
          </div>
        )}

        {/* Visibility */}
        {visibility && (
          <div className="text-center p-3 bg-amber-50 rounded-lg">
            <Eye className="w-5 h-5 text-amber-500 mx-auto mb-1" />
            <div className="text-lg font-semibold text-gray-700">
              {Math.round(visibility / 1000)} km
            </div>
            <div className="text-xs text-gray-500">Visibility</div>
          </div>
        )}

        {/* Rainfall */}
        {(rainfall_1h || rainfall_3h) && (
          <div className="text-center p-3 bg-indigo-50 rounded-lg">
            <CloudRain className="w-5 h-5 text-indigo-500 mx-auto mb-1" />
            <div className="text-lg font-semibold text-gray-700">
              {rainfall_1h ? `${rainfall_1h} mm` : rainfall_3h ? `${rainfall_3h} mm` : '0 mm'}
            </div>
            <div className="text-xs text-gray-500">
              {rainfall_1h ? 'Rain (1h)' : 'Rain (3h)'}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}