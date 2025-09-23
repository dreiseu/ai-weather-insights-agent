import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('🚨 API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging and error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`);
    return response;
  },
  (error) => {
    console.error('🚨 API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * Weather API service functions
 */
export const weatherApi = {
  /**
   * Test connection to backend
   */
  async testConnection() {
    try {
      console.log('🧪 Testing backend connection...');
      const response = await api.post('/test-connection', {
        test: 'frontend-backend connection',
        timestamp: new Date().toISOString()
      });
      console.log('✅ Backend connection test successful:', response.data);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('❌ Backend connection test failed:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Get weather insights for a single location
   * @param {Object} params - Request parameters
   * @param {string} params.location - Location name (e.g., "Manila, PH")
   * @param {string} params.audience - Target audience: "farmers", "officials", "general"
   * @param {number} [params.latitude] - Optional latitude coordinate
   * @param {number} [params.longitude] - Optional longitude coordinate
   * @returns {Promise} Weather insights response
   */
  async getWeatherInsights({ location, audience = 'general', latitude, longitude }) {
    try {
      const response = await api.post('/weather/insights', {
        location,
        audience,
        latitude,
        longitude,
      });
      return response.data;
    } catch (error) {
      throw this.handleApiError(error);
    }
  },

  /**
   * Get weather insights for multiple locations
   * @param {Object} params - Request parameters
   * @param {string[]} params.locations - Array of location names
   * @param {string} params.audience - Target audience
   * @returns {Promise} Batch weather insights response
   */
  async getBatchWeatherInsights({ locations, audience = 'general' }) {
    try {
      const response = await api.post('/weather/batch', {
        locations,
        audience,
      });
      return response.data;
    } catch (error) {
      throw this.handleApiError(error);
    }
  },

  /**
   * Get system health status
   * @returns {Promise} Health status response
   */
  async getHealthStatus() {
    try {
      const response = await axios.get('http://localhost:8000/health');
      return response.data;
    } catch (error) {
      throw this.handleApiError(error);
    }
  },

  /**
   * Get detailed system status
   * @returns {Promise} System status response
   */
  async getSystemStatus() {
    try {
      const response = await api.get('/system/status');
      return response.data;
    } catch (error) {
      throw this.handleApiError(error);
    }
  },

  /**
   * Handle API errors consistently
   * @param {Error} error - Axios error object
   * @returns {Object} Formatted error object
   */
  handleApiError(error) {
    if (error.response) {
      // Server responded with error status
      return {
        type: 'API_ERROR',
        status: error.response.status,
        message: error.response.data?.message || error.response.data?.detail || 'API request failed',
        details: error.response.data,
      };
    } else if (error.request) {
      // Request made but no response received
      return {
        type: 'NETWORK_ERROR',
        message: 'Unable to connect to weather service. Please check if the backend is running.',
        details: error.message,
      };
    } else {
      // Something else happened
      return {
        type: 'UNKNOWN_ERROR',
        message: error.message || 'An unexpected error occurred',
        details: error,
      };
    }
  },
};

/**
 * Utility functions for working with weather data
 */
export const weatherUtils = {
  /**
   * Get priority color class for recommendations
   * @param {string} priority - Priority level: "critical", "high", "medium", "low"
   * @returns {string} Tailwind CSS color classes
   */
  getPriorityColor(priority) {
    const colors = {
      critical: 'bg-red-100 text-red-800 border-red-200',
      high: 'bg-orange-100 text-orange-800 border-orange-200',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      low: 'bg-blue-100 text-blue-800 border-blue-200',
    };
    return colors[priority] || colors.low;
  },

  /**
   * Get timing indicator for recommendations
   * @param {string} timing - Timing: "now", "within_24h", "this_week", "next_week"
   * @returns {Object} Timing display info
   */
  getTimingInfo(timing) {
    const timingMap = {
      now: { label: 'NOW', color: 'text-red-600', icon: '🔴' },
      within_24h: { label: '24H', color: 'text-orange-600', icon: '🟡' },
      this_week: { label: 'WEEK', color: 'text-yellow-600', icon: '🟢' },
      next_week: { label: 'LATER', color: 'text-blue-600', icon: '🔵' },
    };
    return timingMap[timing] || timingMap.this_week;
  },

  /**
   * Format temperature for display
   * @param {number} temp - Temperature in Celsius
   * @returns {string} Formatted temperature
   */
  formatTemperature(temp) {
    return `${Math.round(temp)}°C`;
  },

  /**
   * Format date for display
   * @param {string|Date} date - Date to format
   * @returns {string} Formatted date
   */
  formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  },

  /**
   * Get weather condition icon
   * @param {string} condition - Weather condition
   * @returns {string} Emoji icon
   */
  getWeatherIcon(condition) {
    const icons = {
      Clear: '☀️',
      Clouds: '☁️',
      Rain: '🌧️',
      Drizzle: '🌦️',
      Thunderstorm: '⛈️',
      Snow: '❄️',
      Mist: '🌫️',
      Fog: '🌫️',
      Haze: '🌫️',
    };
    return icons[condition] || '🌤️';
  },

  /**
   * Validate location input
   * @param {string} location - Location string
   * @returns {boolean} Whether location is valid
   */
  isValidLocation(location) {
    return typeof location === 'string' && location.trim().length >= 2;
  },
};