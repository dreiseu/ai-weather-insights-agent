import { useState, useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import { 
  CloudSun, 
  Users, 
  Search, 
  RefreshCw, 
  AlertCircle,
  Activity,
  MapPin,
  Zap
} from 'lucide-react';
import WeatherCard from './WeatherCard';
import InsightsPanel from './InsightsPanel';
import useWeatherData from '../hooks/useWeatherData';
import { weatherApi, weatherUtils } from '../services/weatherApi';

export default function Dashboard() {
  const [location, setLocation] = useState('');
  const [audience, setAudience] = useState('general');
  const [systemStatus, setSystemStatus] = useState(null);
  
  const { 
    loading, 
    data, 
    error, 
    fetchWeatherInsights, 
    retry,
    clearData 
  } = useWeatherData();

  // Fetch system status on component mount
  useEffect(() => {
    const checkSystemStatus = async () => {
      try {
        const status = await weatherApi.getSystemStatus();
        setSystemStatus(status);
      } catch (err) {
        console.warn('Could not fetch system status:', err);
      }
    };

    checkSystemStatus();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!weatherUtils.isValidLocation(location)) {
      return;
    }
    await fetchWeatherInsights(location, audience);
  };

  const handleLocationSuggestion = (suggestedLocation) => {
    setLocation(suggestedLocation);
  };

  const audienceOptions = [
    { value: 'general', label: 'General Public', icon: '👥' },
    { value: 'farmers', label: 'Farmers', icon: '👨‍🌾' },
    { value: 'officials', label: 'Local Officials', icon: '🏛️' },
  ];

  const locationSuggestions = [
    'Manila, PH',
    'Cebu, PH', 
    'Davao, PH',
    'Iloilo, PH',
    'Baguio, PH',
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster 
        position="top-right" 
        toastOptions={{
          duration: 4000,
          style: {
            background: '#fff',
            color: '#374151',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
          },
        }}
      />
      
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <CloudSun className="w-8 h-8 text-weather-blue" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">
                    AI Weather Insights Agent
                  </h1>
                  <p className="text-sm text-gray-600">
                    Transform weather data into actionable insights for rural communities
                  </p>
                </div>
              </div>
            </div>
            
            {/* System Status */}
            {systemStatus && (
              <div className="flex items-center space-x-2 text-sm">
                <Activity className="w-4 h-4 text-green-500" />
                <span className="text-green-600">
                  {systemStatus.workflow === 'operational' ? 'System Online' : 'System Issues'}
                </span>
                {systemStatus.knowledge_base_stats && (
                  <span className="text-gray-500">
                    • {systemStatus.knowledge_base_stats.total_documents} knowledge items
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Section */}
        <div className="card mb-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Location Input */}
              <div>
                <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
                  <MapPin className="w-4 h-4 inline mr-1" />
                  Location
                </label>
                <input
                  type="text"
                  id="location"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="Enter city name (e.g., Manila, PH)"
                  className="input-field"
                  disabled={loading}
                />
                
                {/* Location Suggestions */}
                <div className="mt-2 flex flex-wrap gap-2">
                  {locationSuggestions.map((suggestion) => (
                    <button
                      key={suggestion}
                      type="button"
                      onClick={() => handleLocationSuggestion(suggestion)}
                      className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-2 py-1 rounded transition-colors"
                      disabled={loading}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>

              {/* Audience Selection */}
              <div>
                <label htmlFor="audience" className="block text-sm font-medium text-gray-700 mb-2">
                  <Users className="w-4 h-4 inline mr-1" />
                  Target Audience
                </label>
                <select
                  id="audience"
                  value={audience}
                  onChange={(e) => setAudience(e.target.value)}
                  className="input-field"
                  disabled={loading}
                >
                  {audienceOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.icon} {option.label}
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-xs text-gray-500">
                  Recommendations will be tailored for the selected audience
                </p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <button
                  type="submit"
                  disabled={loading || !weatherUtils.isValidLocation(location)}
                  className="btn-primary flex items-center space-x-2"
                >
                  {loading ? (
                    <>
                      <div className="loading-spinner w-4 h-4"></div>
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4" />
                      <span>Get Weather Insights</span>
                    </>
                  )}
                </button>

                {data && (
                  <button
                    type="button"
                    onClick={clearData}
                    className="btn-secondary"
                    disabled={loading}
                  >
                    Clear Results
                  </button>
                )}
              </div>

              {error && (
                <button
                  type="button"
                  onClick={retry}
                  className="btn-secondary flex items-center space-x-2"
                  disabled={loading}
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Retry</span>
                </button>
              )}
            </div>
          </form>
        </div>

        {/* Error Display */}
        {error && (
          <div className="card mb-8 border-red-200 bg-red-50">
            <div className="flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="text-sm font-medium text-red-800 mb-1">
                  Analysis Failed
                </h3>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="card mb-8 text-center">
            <div className="flex items-center justify-center space-x-3">
              <div className="loading-spinner w-6 h-6"></div>
              <div>
                <p className="text-lg font-medium text-gray-700">
                  Analyzing Weather Data...
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  Running AI agents: Data → Forecast → Advice
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {data && data.success && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 fade-in">
            {/* Weather Card */}
            <div className="lg:col-span-1">
              <WeatherCard weatherData={{
                ...data.current_weather,
                location: data.location,
                weather_condition: data.current_weather.condition,
                description: data.current_weather.condition,
                timestamp: data.analysis_time,
                pressure: null,
                wind_speed: null
              }} />
              
              {/* Data Quality Card */}
              {data.data_quality && (
                <div className="card mt-6">
                  <div className="flex items-center space-x-2 mb-3">
                    <Zap className="w-5 h-5 text-yellow-500" />
                    <h3 className="text-lg font-semibold">Data Quality</h3>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Quality Score</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full" 
                            style={{ width: `${data.data_quality.quality_score * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">
                          {Math.round(data.data_quality.quality_score * 100)}%
                        </span>
                      </div>
                    </div>
                    
                    {data.data_quality.anomalies_detected.length > 0 && (
                      <div>
                        <p className="text-sm text-gray-600 mb-1">Issues Detected:</p>
                        <ul className="text-xs text-red-600 space-y-1">
                          {data.data_quality.anomalies_detected.map((anomaly, index) => (
                            <li key={index}>• {anomaly}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Insights Panel */}
            <div className="lg:col-span-2">
              <InsightsPanel
                forecastData={{
                  insights: Array.isArray(data.recommendations) ? data.recommendations : [],
                  forecasts: Array.isArray(data.recommendations) ? data.recommendations : [],
                  weather_trends: Array.isArray(data.risk_alerts) ?
                    data.risk_alerts.map(alert => ({
                      trend: alert,
                      severity: 'medium',
                      timeframe: '24h'
                    })) : [],
                  risk_alerts: Array.isArray(data.risk_alerts) ? data.risk_alerts : []
                }}
                recommendationsData={{
                  recommendations: Array.isArray(data.recommendations) ? data.recommendations : [],
                  priority_summary: data.summary || "",
                  action_checklist: Array.isArray(data.recommendations) ?
                    data.recommendations.map(rec => {
                      const timing = rec.timing === 'today' ? '24H' :
                                   rec.timing === 'immediate' ? 'NOW' :
                                   rec.timing === 'this week' ? 'WEEK' : '24H';
                      return `${timing}: ${rec.title}`;
                    }) : []
                }}
                currentWeather={data.current_weather}
              />
            </div>
          </div>
        )}

        {/* Demo Instructions */}
        {!data && !loading && (
          <div className="card text-center">
            <CloudSun className="w-16 h-16 text-weather-blue mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Welcome to AI Weather Insights
            </h2>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              Enter a location above to get AI-powered weather insights tailored for your audience. 
              Our system transforms raw weather data into actionable recommendations using a multi-agent workflow.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8 text-left">
              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl mb-2">🔍</div>
                <h3 className="font-semibold text-gray-900 mb-1">Data Agent</h3>
                <p className="text-sm text-gray-600">
                  Analyzes and validates weather data quality from OpenWeather API
                </p>
              </div>
              
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="text-2xl mb-2">📈</div>
                <h3 className="font-semibold text-gray-900 mb-1">Forecast Agent</h3>
                <p className="text-sm text-gray-600">
                  Predicts weather implications and identifies risks for your area
                </p>
              </div>
              
              <div className="p-4 bg-yellow-50 rounded-lg">
                <div className="text-2xl mb-2">💡</div>
                <h3 className="font-semibold text-gray-900 mb-1">Advice Agent</h3>
                <p className="text-sm text-gray-600">
                  Generates actionable recommendations tailored to your audience
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}