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
    <div className="space-y-6">
      {/* Main Weather Card */}
      <div className="card card-hover">
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center space-x-3">
            <MapPin className="w-6 h-6 text-gray-500" />
            <h3 className="text-xl font-semibold text-gray-900">{location}</h3>
          </div>
          <div className="text-4xl">{weatherIcon}</div>
        </div>

        {/* Main Weather Info - Expanded */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          {/* Temperature Section */}
          <div className="text-center md:text-left">
            <div className="text-5xl font-bold text-weather-blue mb-2">
              {formattedTemp}
            </div>
            {feels_like && (
              <div className="text-lg text-gray-600 mb-1">
                Feels like {weatherUtils.formatTemperature(feels_like)}
              </div>
            )}
            <div className="text-lg text-gray-500 capitalize">{description}</div>
          </div>

          {/* Weather Condition Section */}
          <div className="text-center md:text-right">
            <div className="text-2xl font-semibold text-gray-700 mb-2">
              {weather_condition}
            </div>
            {cloudiness !== null && (
              <div className="text-lg text-gray-600 mb-1">
                {cloudiness}% cloud coverage
              </div>
            )}
            <div className="flex items-center justify-center md:justify-end text-lg text-gray-500">
              <Clock className="w-5 h-5 mr-2" />
              {formattedDate}
            </div>
          </div>
        </div>
      </div>

      {/* Weather Parameters Card */}
      <div className="card">
        <h4 className="text-lg font-semibold text-gray-900 mb-6">Current Conditions</h4>

        {/* Weather Details Grid - More Spacious */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
          {/* Humidity */}
          <div className="text-center p-6 bg-blue-50 rounded-xl border border-blue-100">
            <Droplets className="w-8 h-8 text-blue-500 mx-auto mb-3" />
            <div className="text-2xl font-bold text-gray-700 mb-1">{humidity}%</div>
            <div className="text-sm text-gray-600 font-medium">Humidity</div>
          </div>

          {/* Wind Speed */}
          {wind_speed && (
            <div className="text-center p-6 bg-green-50 rounded-xl border border-green-100">
              <Wind className="w-8 h-8 text-green-500 mx-auto mb-3" />
              <div className="text-2xl font-bold text-gray-700 mb-1">
                {Math.round(wind_speed)} m/s
              </div>
              <div className="text-sm text-gray-600 font-medium">Wind Speed</div>
            </div>
          )}

          {/* Wind Direction */}
          {wind_direction && (
            <div className="text-center p-6 bg-cyan-50 rounded-xl border border-cyan-100">
              <Compass className="w-8 h-8 text-cyan-500 mx-auto mb-3" />
              <div className="text-2xl font-bold text-gray-700 mb-1">
                {wind_direction}°
              </div>
              <div className="text-sm text-gray-600 font-medium">Wind Direction</div>
            </div>
          )}

          {/* Pressure */}
          {pressure && (
            <div className="text-center p-6 bg-purple-50 rounded-xl border border-purple-100">
              <Gauge className="w-8 h-8 text-purple-500 mx-auto mb-3" />
              <div className="text-2xl font-bold text-gray-700 mb-1">
                {Math.round(pressure)} hPa
              </div>
              <div className="text-sm text-gray-600 font-medium">Pressure</div>
            </div>
          )}

          {/* Visibility */}
          {visibility && (
            <div className="text-center p-6 bg-amber-50 rounded-xl border border-amber-100">
              <Eye className="w-8 h-8 text-amber-500 mx-auto mb-3" />
              <div className="text-2xl font-bold text-gray-700 mb-1">
                {Math.round(visibility / 1000)} km
              </div>
              <div className="text-sm text-gray-600 font-medium">Visibility</div>
            </div>
          )}

          {/* Rainfall */}
          {(rainfall_1h || rainfall_3h) && (
            <div className="text-center p-6 bg-indigo-50 rounded-xl border border-indigo-100">
              <CloudRain className="w-8 h-8 text-indigo-500 mx-auto mb-3" />
              <div className="text-2xl font-bold text-gray-700 mb-1">
                {rainfall_1h ? `${rainfall_1h} mm` : rainfall_3h ? `${rainfall_3h} mm` : '0 mm'}
              </div>
              <div className="text-sm text-gray-600 font-medium">
                {rainfall_1h ? 'Rainfall (1h)' : 'Rainfall (3h)'}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}