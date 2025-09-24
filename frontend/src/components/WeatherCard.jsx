import { weatherUtils } from '../services/weatherApi';
import { 
  Thermometer, 
  Droplets, 
  Wind, 
  Gauge,
  MapPin,
  Clock
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

  const {
    location,
    temperature,
    humidity,
    pressure,
    wind_speed,
    weather_condition,
    description,
    timestamp
  } = weatherData;

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
          <div className="text-sm text-gray-500 capitalize">{description}</div>
        </div>

        {/* Weather Condition */}
        <div className="text-center">
          <div className="text-lg font-semibold text-gray-700 mb-1">
            {weather_condition}
          </div>
          <div className="flex items-center justify-center text-sm text-gray-500">
            <Clock className="w-4 h-4 mr-1" />
            {formattedDate}
          </div>
        </div>
      </div>

      {/* Weather Details Grid */}
      <div className="grid grid-cols-3 gap-4">
        {/* Humidity */}
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <Droplets className="w-5 h-5 text-blue-500 mx-auto mb-1" />
          <div className="text-lg font-semibold text-gray-700">{humidity}%</div>
          <div className="text-xs text-gray-500">Humidity</div>
        </div>

        {/* Wind - only show if available */}
        {wind_speed && (
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <Wind className="w-5 h-5 text-green-500 mx-auto mb-1" />
            <div className="text-lg font-semibold text-gray-700">
              {Math.round(wind_speed)} m/s
            </div>
            <div className="text-xs text-gray-500">Wind</div>
          </div>
        )}

        {/* Pressure - only show if available */}
        {pressure && (
          <div className="text-center p-3 bg-purple-50 rounded-lg">
            <Gauge className="w-5 h-5 text-purple-500 mx-auto mb-1" />
            <div className="text-lg font-semibold text-gray-700">
              {Math.round(pressure)} hPa
            </div>
            <div className="text-xs text-gray-500">Pressure</div>
          </div>
        )}
      </div>
    </div>
  );
}