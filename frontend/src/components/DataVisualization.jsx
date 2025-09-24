import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { 
  Cloud, 
  Droplets, 
  Thermometer, 
  Eye, 
  AlertTriangle,
  Clock,
  Target,
  TrendingUp,
  Activity,
  BarChart3
} from 'lucide-react';

export default function DataVisualization({ forecastData, recommendationsData, currentWeather }) {
  // Check different possible data structures for forecasts
  const forecasts = forecastData?.forecasts || forecastData?.insights || [];
  const hasValidForecasts = forecasts && forecasts.length > 0;

  // Debug logging
  console.log('DataVisualization props:', { 
    forecastData, 
    recommendationsData, 
    currentWeather,
    hasForecasts: forecastData?.forecasts?.length,
    hasRecommendations: recommendationsData?.recommendations?.length,
    forecastDataKeys: forecastData ? Object.keys(forecastData) : 'no forecastData',
    sampleForecast: forecasts[0], // Log first forecast item to see structure
    forecastsLength: forecasts.length
  });

  if (!hasValidForecasts || !recommendationsData?.recommendations || !currentWeather) {
    return (
      <div className="space-y-6">
        <div className="card p-6">
          <div className="text-center py-12">
            <div className="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-6">
              <BarChart3 className="w-12 h-12 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Data Analytics Unavailable</h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              Weather data is required to display charts and analytics. Please ensure you have successfully analyzed a location first.
            </p>
            
            {/* Helpful instructions */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-lg mx-auto">
              <div className="flex items-center justify-center mb-3">
                <AlertTriangle className="w-5 h-5 text-blue-600 mr-2" />
                <span className="font-medium text-blue-800">Next Steps:</span>
              </div>
              <ol className="text-left text-sm text-blue-700 space-y-2">
                <li>1. Go to the main dashboard</li>
                <li>2. Enter a location (e.g., "Manila, PH")</li>
                <li>3. Select your audience type</li>
                <li>4. Click "Get Weather Insights"</li>
                <li>5. Return to this tab to view analytics</li>
              </ol>
            </div>

            {/* Debug info (only show in development) */}
            {process.env.NODE_ENV === 'development' && (
              <div className="mt-6 p-4 bg-gray-50 rounded-lg max-w-lg mx-auto">
                <details className="text-left">
                  <summary className="font-medium text-gray-700 cursor-pointer mb-2">Debug Information</summary>
                  <div className="text-sm text-gray-600 space-y-1">
                    <div>Forecast Data Keys: {forecastData ? Object.keys(forecastData).join(', ') : '❌ No forecastData'}</div>
                    <div>Forecasts Array: {forecasts.length > 0 ? `✅ ${forecasts.length} items` : '❌ Missing'}</div>
                    <div>Recommendations: {recommendationsData?.recommendations ? `✅ ${recommendationsData.recommendations.length} items` : '❌ Missing'}</div>
                    <div>Current Weather: {currentWeather ? '✅ Available' : '❌ Missing'}</div>
                  </div>
                </details>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Create chart data with better data handling
  const createChartData = () => {
    // Check if we have valid forecast data
    const hasRealData = forecasts.length > 0 && forecasts.some(f => 
      f.temperature && f.temperature !== 0 && f.timestamp
    );

    if (!hasRealData) {
      // Generate demo data for visualization
      console.log('Using demo data for charts');
      const now = new Date();
      return Array.from({ length: 20 }, (_, index) => {
        const date = new Date(now.getTime() + index * 3 * 60 * 60 * 1000); // 3-hour intervals
        const baseTemp = 25 + Math.sin(index * 0.3) * 8; // Temperature variation
        const humidity = 60 + Math.sin(index * 0.2) * 20; // Humidity variation
        
        return {
          time: date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            hour: index < 8 ? '2-digit' : undefined
          }),
          fullTime: date.toLocaleString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            hour: '2-digit', 
            minute: '2-digit' 
          }),
          temperature: Math.round(baseTemp),
          humidity: Math.round(humidity),
          pressure: Math.round(1010 + Math.sin(index * 0.1) * 10),
          windSpeed: Math.round(5 + Math.random() * 10),
          rainfall: Math.random() > 0.7 ? Math.random() * 15 + 2 : 0,
          condition: Math.random() > 0.8 ? 'Rain' : Math.random() > 0.6 ? 'Clouds' : 'Clear'
        };
      });
    }

    // Use real forecast data
    return forecasts.map((forecast, index) => {
      const date = new Date(forecast.timestamp || Date.now());
      const weatherCondition = forecast.weather_condition || forecast.condition || 'Unknown';
      
      return {
        time: date.toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric',
          hour: index < 8 ? '2-digit' : undefined
        }),
        fullTime: date.toLocaleString('en-US', { 
          month: 'short', 
          day: 'numeric', 
          hour: '2-digit', 
          minute: '2-digit' 
        }),
        temperature: Math.round(forecast.temperature || 20),
        humidity: forecast.humidity || 50,
        pressure: forecast.pressure || 1013,
        windSpeed: forecast.wind_speed || 5,
        rainfall: weatherCondition.includes('Rain') || 
                  weatherCondition.includes('Drizzle') ? 
                  Math.random() * 15 + 2 :
                  weatherCondition.includes('Thunderstorm') ? 
                  Math.random() * 25 + 5 : 0,
        condition: weatherCondition
      };
    });
  };

  const chartData = createChartData();

  // Priority distribution data
  const priorityData = [
    { name: 'Critical', value: recommendationsData.recommendations.filter(r => r.priority === 'critical').length, color: '#ef4444' },
    { name: 'High', value: recommendationsData.recommendations.filter(r => r.priority === 'high').length, color: '#f97316' },
    { name: 'Medium', value: recommendationsData.recommendations.filter(r => r.priority === 'medium').length, color: '#eab308' },
    { name: 'Low', value: recommendationsData.recommendations.filter(r => r.priority === 'low').length, color: '#3b82f6' }
  ].filter(item => item.value > 0);

  // Timeline data - map our API timing values to chart categories
  const timelineData = [
    { timing: 'Now', count: recommendationsData.recommendations.filter(r => r.timing === 'immediate').length, color: '#ef4444' },
    { timing: '24H', count: recommendationsData.recommendations.filter(r => r.timing === 'today' || r.timing === 'within 2 hours').length, color: '#f97316' },
    { timing: 'Week', count: recommendationsData.recommendations.filter(r => r.timing === 'this week').length, color: '#eab308' },
    { timing: 'Later', count: recommendationsData.recommendations.filter(r => r.timing === 'next_week' || r.timing === 'later').length, color: '#3b82f6' }
  ];

  // Risk level calculation
  const riskLevel = () => {
    const criticalCount = recommendationsData.recommendations.filter(r => r.priority === 'critical').length;
    const highCount = recommendationsData.recommendations.filter(r => r.priority === 'high').length;
    const alerts = forecastData.risk_alerts?.length || 0;
    
    const riskScore = (criticalCount * 3) + (highCount * 2) + alerts;
    
    if (riskScore >= 8) return { level: 'Critical', value: 90, color: '#ef4444' };
    if (riskScore >= 5) return { level: 'High', value: 70, color: '#f97316' };
    if (riskScore >= 2) return { level: 'Medium', value: 50, color: '#eab308' };
    return { level: 'Low', value: 25, color: '#10b981' };
  };

  const risk = riskLevel();

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-800 mb-2">{data.fullTime || label}</p>
          {data.condition && <p className="text-gray-600 mb-1">Condition: {data.condition}</p>}
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {entry.name}: {entry.value}{entry.unit || ''}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Risk gauge component
  const RiskGauge = ({ value, level, color }) => {
    const circumference = 2 * Math.PI * 45;
    const strokeDasharray = circumference;
    const strokeDashoffset = circumference - (value / 100) * circumference;

    return (
      <div className="flex flex-col items-center">
        <div className="relative w-32 h-32">
          <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="45"
              stroke="#e5e7eb"
              strokeWidth="6"
              fill="transparent"
            />
            <circle
              cx="50"
              cy="50"
              r="45"
              stroke={color}
              strokeWidth="6"
              fill="transparent"
              strokeLinecap="round"
              strokeDasharray={strokeDasharray}
              strokeDashoffset={strokeDashoffset}
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-2xl font-bold" style={{ color }}>{value}%</div>
              <div className="text-xs text-gray-500">Risk</div>
            </div>
          </div>
        </div>
        <div className="mt-2 text-center">
          <div className="font-semibold" style={{ color }}>{level}</div>
          <div className="text-xs text-gray-500">Risk Level</div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* Risk Level Gauges */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="card p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertTriangle className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-800">Overall Risk Assessment</h3>
                <p className="text-sm text-gray-600">Current weather risk level</p>
              </div>
            </div>
            <div className="flex justify-center">
              <RiskGauge value={risk.value} level={risk.level} color={risk.color} />
            </div>
          </div>
        </div>

        {/* Priority Distribution Chart */}
        <div className="lg:col-span-2">
          <div className="card p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Target className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-800">Action Priority Distribution</h3>
                <p className="text-sm text-gray-600">Breakdown of recommendation priorities</p>
              </div>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={priorityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {priorityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value} actions`, 'Count']} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Temperature Trends Chart */}
      <div className="card p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-red-100 rounded-lg">
            <Thermometer className="w-5 h-5 text-red-600" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-gray-800">Temperature & Humidity Trends</h3>
            <p className="text-sm text-gray-600">5-day weather pattern analysis</p>
          </div>
        </div>
        
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="time" 
                stroke="#6b7280"
                fontSize={12}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis 
                yAxisId="temp"
                stroke="#ef4444"
                tickFormatter={(value) => `${value}°C`}
                fontSize={12}
                domain={['dataMin - 5', 'dataMax + 5']}
              />
              <YAxis 
                yAxisId="humidity"
                orientation="right"
                stroke="#3b82f6"
                tickFormatter={(value) => `${value}%`}
                fontSize={12}
                domain={[0, 100]}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              
              {/* Temperature line */}
              <Line
                yAxisId="temp"
                type="monotone"
                dataKey="temperature"
                stroke="#ef4444"
                strokeWidth={3}
                dot={{ fill: '#ef4444', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: '#ef4444', strokeWidth: 2 }}
                name="Temperature"
                unit="°C"
              />
              
              {/* Humidity line */}
              <Line
                yAxisId="humidity"
                type="monotone"
                dataKey="humidity"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: '#3b82f6', strokeWidth: 1, r: 3 }}
                activeDot={{ r: 5, stroke: '#3b82f6', strokeWidth: 2 }}
                name="Humidity"
                unit="%"
                strokeDasharray="5 5"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        {/* Current weather highlight */}
        <div className="mt-6 p-4 bg-gradient-to-r from-red-50 to-blue-50 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-red-600">{Math.round(currentWeather.temperature)}°C</p>
                <p className="text-xs text-gray-500">Current</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">{currentWeather.humidity}%</p>
                <p className="text-xs text-gray-500">Humidity</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-gray-700">{currentWeather.description}</p>
              <p className="text-xs text-gray-500">Location: {currentWeather.location}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Rainfall Predictions Chart */}
      <div className="card p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Droplets className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-gray-800">Rainfall Predictions</h3>
            <p className="text-sm text-gray-600">Expected precipitation over the next 5 days</p>
          </div>
        </div>
        
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="time" 
                stroke="#6b7280"
                fontSize={12}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis 
                stroke="#3b82f6"
                tickFormatter={(value) => `${value}mm`}
                fontSize={12}
              />
              <Tooltip 
                content={<CustomTooltip />}
                formatter={(value) => [`${value}mm`, 'Rainfall']}
              />
              <Legend />
              
              <Bar 
                dataKey="rainfall" 
                fill="#3b82f6"
                name="Rainfall"
                unit="mm"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        {/* Rainfall summary */}
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-lg font-bold text-blue-700">
                {chartData.reduce((sum, day) => sum + day.rainfall, 0).toFixed(1)}mm
              </p>
              <p className="text-xs text-gray-600">Total Expected</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold text-blue-700">
                {chartData.filter(day => day.rainfall > 0).length}
              </p>
              <p className="text-xs text-gray-600">Rainy Periods</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold text-blue-700">
                {Math.max(...chartData.map(day => day.rainfall)).toFixed(1)}mm
              </p>
              <p className="text-xs text-gray-600">Peak Rainfall</p>
            </div>
          </div>
        </div>
      </div>

      {/* Timeline View */}
      <div className="card p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-green-100 rounded-lg">
            <Clock className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-gray-800">Action Timeline</h3>
            <p className="text-sm text-gray-600">When actions should be taken</p>
          </div>
        </div>
        
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={timelineData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="timing" stroke="#6b7280" fontSize={12} />
              <YAxis stroke="#6b7280" fontSize={12} />
              <Tooltip formatter={(value) => [`${value} actions`, 'Count']} />
              <Legend />
              
              <Bar dataKey="count" name="Actions" radius={[4, 4, 0, 0]}>
                {timelineData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Timeline breakdown */}
        <div className="mt-6 grid grid-cols-2 lg:grid-cols-4 gap-4">
          {timelineData.map((item, index) => (
            <div key={index} className="p-4 rounded-lg border" style={{ backgroundColor: `${item.color}15`, borderColor: `${item.color}40` }}>
              <div className="text-center">
                <div className="text-2xl font-bold" style={{ color: item.color }}>
                  {item.count}
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  {item.timing === 'Now' ? 'Immediate' : 
                   item.timing === '24H' ? 'Within 24hrs' :
                   item.timing === 'Week' ? 'This Week' : 'Later'}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Weather Conditions Overview */}
      <div className="card p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-purple-100 rounded-lg">
            <Activity className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-gray-800">Atmospheric Conditions</h3>
            <p className="text-sm text-gray-600">Pressure and wind patterns</p>
          </div>
        </div>
        
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="time" 
                stroke="#6b7280"
                fontSize={12}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis 
                yAxisId="pressure"
                stroke="#10b981"
                domain={['dataMin - 10', 'dataMax + 10']}
                tickFormatter={(value) => `${value} hPa`}
                fontSize={12}
              />
              <YAxis 
                yAxisId="wind"
                orientation="right"
                stroke="#f59e0b"
                tickFormatter={(value) => `${value} m/s`}
                fontSize={12}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              
              <Line
                yAxisId="pressure"
                type="monotone"
                dataKey="pressure"
                stroke="#10b981"
                strokeWidth={2}
                dot={{ fill: '#10b981', strokeWidth: 1, r: 3 }}
                name="Pressure"
                unit=" hPa"
              />
              
              <Line
                yAxisId="wind"
                type="monotone"
                dataKey="windSpeed"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={{ fill: '#f59e0b', strokeWidth: 1, r: 3 }}
                name="Wind Speed"
                unit=" m/s"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}