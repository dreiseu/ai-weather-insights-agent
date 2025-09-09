import { useState, useCallback } from 'react';
import { weatherApi } from '../services/weatherApi';
import toast from 'react-hot-toast';

export default function useWeatherData() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [lastRequest, setLastRequest] = useState(null);

  const fetchWeatherInsights = useCallback(async (location, audience = 'general') => {
    if (!location || !location.trim()) {
      toast.error('Please enter a valid location');
      return;
    }

    setLoading(true);
    setError(null);
    
    const requestData = { location: location.trim(), audience };
    setLastRequest(requestData);

    try {
      console.log('🌦️ Fetching weather insights for:', requestData);
      
      const result = await weatherApi.getWeatherInsights(requestData);
      
      if (result.success) {
        setData(result);
        toast.success(`Weather insights loaded for ${location}`, {
          duration: 3000,
          icon: '✅',
        });
        console.log('✅ Weather insights received:', result);
      } else {
        const errorMessage = result.error_message || 'Failed to get weather insights';
        setError(errorMessage);
        toast.error(errorMessage);
        console.error('❌ Weather API returned error:', result);
      }
    } catch (err) {
      console.error('❌ Error fetching weather insights:', err);
      
      let errorMessage = 'Failed to fetch weather insights';
      
      if (err.type === 'NETWORK_ERROR') {
        errorMessage = 'Cannot connect to weather service. Please check if the backend is running.';
      } else if (err.type === 'API_ERROR') {
        errorMessage = err.message || 'API request failed';
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      toast.error(errorMessage, {
        duration: 5000,
        icon: '🚨',
      });
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchBatchInsights = useCallback(async (locations, audience = 'general') => {
    if (!locations || locations.length === 0) {
      toast.error('Please provide at least one location');
      return;
    }

    setLoading(true);
    setError(null);
    
    const requestData = { locations, audience };
    setLastRequest(requestData);

    try {
      console.log('🌦️ Fetching batch weather insights for:', requestData);
      
      const result = await weatherApi.getBatchWeatherInsights(requestData);
      
      setData(result);
      toast.success(`Batch analysis completed for ${locations.length} locations`, {
        duration: 3000,
        icon: '✅',
      });
      console.log('✅ Batch weather insights received:', result);
    } catch (err) {
      console.error('❌ Error fetching batch insights:', err);
      
      let errorMessage = 'Failed to fetch batch weather insights';
      
      if (err.type === 'NETWORK_ERROR') {
        errorMessage = 'Cannot connect to weather service. Please check if the backend is running.';
      } else if (err.type === 'API_ERROR') {
        errorMessage = err.message || 'Batch API request failed';
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      toast.error(errorMessage, {
        duration: 5000,
        icon: '🚨',
      });
    } finally {
      setLoading(false);
    }
  }, []);

  const retry = useCallback(() => {
    if (lastRequest) {
      if (Array.isArray(lastRequest.locations)) {
        fetchBatchInsights(lastRequest.locations, lastRequest.audience);
      } else {
        fetchWeatherInsights(lastRequest.location, lastRequest.audience);
      }
    }
  }, [lastRequest, fetchWeatherInsights, fetchBatchInsights]);

  const clearData = useCallback(() => {
    setData(null);
    setError(null);
    setLastRequest(null);
  }, []);

  return {
    loading,
    data,
    error,
    fetchWeatherInsights,
    fetchBatchInsights,
    retry,
    clearData,
    lastRequest,
  };
}