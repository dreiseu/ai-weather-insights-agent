import { useState } from 'react';
import { weatherUtils } from '../services/weatherApi';
import DataVisualization from './DataVisualization';
import { 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle,
  Clock,
  Target,
  Lightbulb,
  List,
  FileText,
  ChevronDown,
  ChevronRight,
  BarChart3
} from 'lucide-react';

export default function InsightsPanel({ forecastData, recommendationsData, currentWeather }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedItems, setExpandedItems] = useState({});

  // Debug logging
  console.log('InsightsPanel props:', {
    forecastData: !!forecastData,
    recommendationsData: !!recommendationsData,
    currentWeather: !!currentWeather,
    forecastKeys: forecastData ? Object.keys(forecastData) : 'none',
    recommendationsKeys: recommendationsData ? Object.keys(recommendationsData) : 'none'
  });

  if (!forecastData || !recommendationsData) {
    return (
      <div className="space-y-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="card">
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-3"></div>
              <div className="space-y-2">
                <div className="h-3 bg-gray-200 rounded"></div>
                <div className="h-3 bg-gray-200 rounded w-4/5"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Handle our actual data structure - both objects have the same data
  const insights = forecastData.recommendations || [];
  const weather_trends = []; // Empty for now - could be populated with trend analysis
  const risk_alerts = forecastData.risk_alerts || [];
  const recommendations = forecastData.recommendations || [];
  const priority_summary = forecastData.summary || "";
  const action_checklist = (forecastData.recommendations || []).map(rec => {
    // Format timing to match what the action checklist expects
    const timing = rec.timing === 'today' ? '24H' :
                  rec.timing === 'immediate' ? 'NOW' :
                  rec.timing === 'within 2 hours' ? '2H' :
                  rec.timing === 'this week' ? 'WEEK' : '24H';
    return `${timing}: ${rec.title}`;
  });

  // Debug extracted data
  console.log('Extracted data:', {
    insights: insights.length,
    risk_alerts: risk_alerts.length,
    recommendations: recommendations.length,
    priority_summary: priority_summary.substring(0, 50) + '...',
    action_checklist: action_checklist.length
  });

  // Sort recommendations by priority and timing
  const sortedRecommendations = [...recommendations].sort((a, b) => {
    const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    const timingOrder = { now: 0, within_24h: 1, this_week: 2, next_week: 3 };
    
    const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
    if (priorityDiff !== 0) return priorityDiff;
    
    return timingOrder[a.timing] - timingOrder[b.timing];
  });

  // Helper function to find related recommendation for a checklist item
  const findRelatedRecommendation = (checklistItem) => {
    if (!checklistItem || !sortedRecommendations || sortedRecommendations.length === 0) {
      return null;
    }

    const [timing, action] = checklistItem.split(': ');
    const actionText = action || checklistItem;

    // Try to match by keywords in the action text
    const keywords = actionText.toLowerCase().split(' ').filter(word => word.length > 3);

    return sortedRecommendations.find(rec => {
      if (!rec || !rec.title || !rec.action) return false;

      const recText = `${rec.title} ${rec.action}`.toLowerCase();
      return keywords.some(keyword => recText.includes(keyword)) ||
             rec.action.toLowerCase().includes(actionText.toLowerCase().substring(0, 20));
    });
  };

  // Toggle expanded state for checklist items
  const toggleExpanded = (index) => {
    setExpandedItems(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Target },
    { id: 'analytics', label: 'Data Analytics', icon: BarChart3 },
    { id: 'checklist', label: 'Action Checklist', icon: List },
    { id: 'insights', label: 'Forecast Insights', icon: Clock }
  ];

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="card p-0">
        <div className="flex flex-wrap border-b border-gray-200">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-weather-blue text-weather-blue bg-blue-50'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{tab.label}</span>
                <span className="sm:hidden">{tab.label.split(' ')[0]}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Priority Summary */}
              <div>
                <div className="flex items-center space-x-2 mb-3">
                  <Target className="w-5 h-5 text-weather-blue" />
                  <h3 className="text-lg font-semibold">Priority Summary</h3>
                </div>
                <p className="text-gray-600 leading-relaxed">{priority_summary}</p>
              </div>

              {/* Risk Alerts */}
              {risk_alerts && risk_alerts.length > 0 && (
                <div>
                  <div className="flex items-center space-x-2 mb-4">
                    <AlertTriangle className="w-5 h-5 text-red-500" />
                    <h3 className="text-lg font-semibold text-red-700">Risk Alerts</h3>
                  </div>
                  <div className="space-y-3">
                    {risk_alerts.map((alert, index) => (
                      <div key={index} className="flex items-start space-x-3 p-4 bg-red-50 border-l-4 border-red-400 rounded-lg">
                        <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                        <p className="text-red-700 text-sm leading-relaxed break-words">{alert}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Weather Trends */}
              {weather_trends && weather_trends.length > 0 && (
                <div>
                  <div className="flex items-center space-x-2 mb-4">
                    <TrendingUp className="w-5 h-5 text-green-500" />
                    <h3 className="text-lg font-semibold">Weather Trends</h3>
                  </div>
                  <div className="space-y-3">
                    {weather_trends.map((trend, index) => (
                      <div key={index} className="flex items-start space-x-3 p-4 bg-green-50 rounded-lg">
                        <TrendingUp className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                        <p className="text-green-700 text-sm leading-relaxed break-words">{trend}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Data Analytics Tab */}
          {activeTab === 'analytics' && (
            <DataVisualization 
              forecastData={forecastData}
              recommendationsData={recommendationsData}
              currentWeather={currentWeather}
            />
          )}

          {/* Action Checklist Tab */}
          {activeTab === 'checklist' && action_checklist && action_checklist.length > 0 && (
            <div>
              <div className="flex items-center space-x-2 mb-6">
                <CheckCircle className="w-5 h-5 text-weather-blue" />
                <h3 className="text-xl font-semibold">Action Checklist</h3>
                <span className="text-sm text-gray-500">({action_checklist.length} items)</span>
              </div>
              <div className="text-sm text-gray-600 mb-4 p-3 bg-blue-50 rounded-lg">
                💡 <strong>Tip:</strong> Click on any action item to see detailed recommendations and explanations.
              </div>
              <div className="space-y-4">
                {action_checklist.map((item, index) => {
                  const [timing, action] = item.split(': ');
                  const timingInfo = weatherUtils.getTimingInfo(
                    timing.includes('NOW') ? 'now' :
                    timing.includes('24H') ? 'within_24h' :
                    timing.includes('WEEK') ? 'this_week' : 'next_week'
                  );
                  const isExpanded = expandedItems[index];
                  const relatedRecommendation = findRelatedRecommendation(item);
                  
                  return (
                    <div key={index} className="bg-white border-2 border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-all">
                      {/* Clickable Header */}
                      <button
                        onClick={() => toggleExpanded(index)}
                        className="w-full p-5 text-left hover:bg-gray-50 transition-colors focus:outline-none focus:bg-gray-50"
                      >
                        <div className="flex items-start space-x-4">
                          <div className={`text-xs font-semibold px-3 py-2 rounded-lg flex-shrink-0 ${
                            timing.includes('NOW') ? 'bg-red-100 text-red-700 border border-red-200' :
                            timing.includes('24H') ? 'bg-orange-100 text-orange-700 border border-orange-200' :
                            timing.includes('WEEK') ? 'bg-yellow-100 text-yellow-700 border border-yellow-200' :
                            'bg-blue-100 text-blue-700 border border-blue-200'
                          }`}>
                            <span className="mr-1">
                              {timing.includes('NOW') ? '🔴' :
                               timing.includes('24H') ? '🟡' :
                               timing.includes('WEEK') ? '🟢' : '🔵'}
                            </span>
                            <span>
                              {timing.includes('NOW') ? 'Immediate' :
                               timing.includes('24H') ? 'Within 24hrs' :
                               timing.includes('WEEK') ? 'This Week' : 'Later'}
                            </span>
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-gray-800 leading-relaxed break-words whitespace-pre-wrap text-base">
                              {action || item}
                            </p>
                            {relatedRecommendation && (
                              <p className="text-sm text-blue-600 mt-2 flex items-center">
                                <span>Click to see detailed recommendation</span>
                              </p>
                            )}
                          </div>
                          <div className="flex-shrink-0 ml-2">
                            {isExpanded ? (
                              <ChevronDown className="w-5 h-5 text-gray-500" />
                            ) : (
                              <ChevronRight className="w-5 h-5 text-gray-500" />
                            )}
                          </div>
                        </div>
                      </button>

                      {/* Expandable Content */}
                      {isExpanded && relatedRecommendation && (
                        <div className="border-t border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50 p-6">
                          <div className="mb-4">
                            <div className="flex flex-wrap items-center gap-3 mb-3">
                              <span className={`badge ${weatherUtils.getPriorityColor(relatedRecommendation.priority || 'medium')} text-sm px-3 py-1`}>
                                {relatedRecommendation.priority?.toUpperCase() || 'MEDIUM'}
                              </span>
                              <span className="text-sm text-gray-600 bg-white px-3 py-1 rounded-full border">
                                {relatedRecommendation.target_audience?.replace('_', ' ') || 'general'}
                              </span>
                            </div>
                            <h4 className="font-bold text-gray-900 mb-3 text-lg">
                              {relatedRecommendation.title || 'Action Item'}
                            </h4>
                          </div>

                          {/* Detailed Action */}
                          <div className="mb-4 p-4 bg-white rounded-lg border border-blue-200">
                            <h5 className="font-semibold text-gray-700 mb-2 text-sm uppercase tracking-wide flex items-center">
                              <CheckCircle className="w-4 h-4 mr-2 text-blue-600" />
                              Detailed Action:
                            </h5>
                            <p className="text-gray-800 leading-relaxed break-words whitespace-pre-wrap">
                              {relatedRecommendation.action || 'No detailed action available'}
                            </p>
                          </div>

                          {/* Reasoning */}
                          {relatedRecommendation.reason && (
                            <div className="mb-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                              <h5 className="font-semibold text-gray-700 mb-2 text-sm uppercase tracking-wide flex items-center">
                                <Lightbulb className="w-4 h-4 mr-2 text-yellow-600" />
                                Why This Matters:
                              </h5>
                              <p className="text-gray-700 leading-relaxed break-words whitespace-pre-wrap">
                                {relatedRecommendation.reason}
                              </p>
                            </div>
                          )}

                          {/* Resources */}
                          {relatedRecommendation.resources_needed && relatedRecommendation.resources_needed.length > 0 && (
                            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                              <h5 className="font-semibold text-gray-700 mb-3 text-sm uppercase tracking-wide">
                                Resources Needed:
                              </h5>
                              <div className="flex flex-wrap gap-2">
                                {relatedRecommendation.resources_needed.map((resource, idx) => (
                                  <span key={idx} className="text-sm bg-green-100 text-green-800 px-3 py-2 rounded-lg border border-green-200 font-medium">
                                    {resource}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {/* No related recommendation found */}
                      {isExpanded && !relatedRecommendation && (
                        <div className="border-t border-gray-200 bg-gray-50 p-6">
                          <div className="text-center text-gray-500">
                            <FileText className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                            <p className="text-sm">No detailed recommendation found for this action item.</p>
                            <p className="text-xs mt-1">This is a general action from the checklist.</p>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}


          {/* Forecast Insights Tab */}
          {activeTab === 'insights' && insights && insights.length > 0 && (
            <div>
              <div className="flex items-center space-x-2 mb-6">
                <Clock className="w-5 h-5 text-weather-blue" />
                <h3 className="text-xl font-semibold">Forecast Insights</h3>
                <span className="text-sm text-gray-500">({insights.length} insights)</span>
              </div>
              <div className="grid gap-6">
                {insights.map((insight, index) => {
                  const priorityColor = weatherUtils.getPriorityColor(insight.priority);
                  
                  return (
                    <div key={index} className="bg-white border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-3">
                        <span className={`badge ${priorityColor} text-sm`}>
                          {insight.priority.toUpperCase()}
                        </span>
                        <div className="text-sm text-gray-500 flex items-center space-x-3">
                          <span>Confidence: {Math.round(insight.confidence * 100)}%</span>
                          <span>•</span>
                          <span>{insight.time_horizon}</span>
                          <span>•</span>
                          <span className="capitalize">{insight.category}</span>
                        </div>
                      </div>
                      <h4 className="font-semibold text-gray-900 mb-3 text-lg">{insight.title}</h4>
                      <p className="text-gray-600 leading-relaxed break-words whitespace-pre-wrap">{insight.description}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}