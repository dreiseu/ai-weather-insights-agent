from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from agents.data_agent import WeatherAnalysis
from agents.forecast_agent import ForecastAnalysis, WeatherInsight


class Recommendation(BaseModel):
    """Individual actionable recommendation"""
    target_audience: str = Field(description="Who this is for: farmers, officials, general_public")
    action_type: str = Field(description="Type: immediate, preparation, planning, monitoring")
    priority: str = Field(description="Priority: critical, high, medium, low")
    title: str = Field(description="Brief recommendation title")
    action: str = Field(description="Specific action to take")
    reasoning: str = Field(description="Why this action is recommended")
    timing: str = Field(description="When to act: now, within_24h, this_week, next_week")
    resources_needed: List[str] = Field(default_factory=list, description="What's needed to act")


class AdviceReport(BaseModel):
    """Complete advice and recommendations report"""
    location: str
    report_time: datetime
    recommendations: List[Recommendation]
    priority_summary: str
    action_checklist: List[str] = Field(default_factory=list)
    contact_suggestions: List[str] = Field(default_factory=list)


class AdviceAgent:
    """AI agent that converts weather insights into actionable recommendations"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self._audience_prompt_cache = {}  # Cache for generated prompts
    
    async def generate_advice(
        self,
        data_analysis: WeatherAnalysis,
        forecast_analysis: ForecastAnalysis,
        audience: str = "general"
    ) -> AdviceReport:
        """Generate comprehensive advice based on weather analysis"""
        
        # Create summaries for AI processing
        data_summary = self._summarize_data_analysis(data_analysis)
        forecast_summary = self._summarize_forecast_analysis(forecast_analysis)
        
        # Create audience-specific prompt
        audience_prompt = await self._create_audience_prompt(audience)
        
        # Get AI-generated advice
        messages = audience_prompt.format_messages(
            data_analysis=data_summary,
            forecast_analysis=forecast_summary
        )
        response = await self.llm.ainvoke(messages)
        
        # Debug: Print the AI response to see what format it's using
        print(f"🔍 AI Advice Response for {audience}:")
        print(f"--- START ADVICE RESPONSE ---")
        print(response.content)
        print(f"--- END ADVICE RESPONSE ---")
        
        # Extract structured recommendations using AI
        recommendations = await self._extract_recommendations_with_ai(response.content, forecast_analysis.location, audience)
        
        # Generate priority summary
        priority_summary = self._create_priority_summary(recommendations)
        
        # Create action checklist
        action_checklist = self._create_action_checklist(recommendations)
        
        # Add contact suggestions
        contact_suggestions = self._generate_contact_suggestions(forecast_analysis.risk_alerts)
        
        return AdviceReport(
            location=forecast_analysis.location,
            report_time=datetime.now(),
            recommendations=recommendations,
            priority_summary=priority_summary,
            action_checklist=action_checklist,
            contact_suggestions=contact_suggestions
        )
    
    def _summarize_data_analysis(self, analysis: WeatherAnalysis) -> str:
        """Summarize data quality analysis for AI"""
        return f"""
        Data Quality Score: {analysis.quality_score:.2f}/1.0
        Issues Detected: {', '.join(analysis.anomalies_detected) if analysis.anomalies_detected else 'None'}
        Key Findings: {analysis.summary[:500]}...
        Data Recommendations: {'; '.join(analysis.recommendations[:3])}
        """
    
    def _summarize_forecast_analysis(self, analysis: ForecastAnalysis) -> str:
        """Summarize forecast analysis for AI"""
        high_priority_insights = [i for i in analysis.insights if i.priority in ['critical', 'high']]
        
        return f"""
        Location: {analysis.location}
        Weather Trends: {'; '.join(analysis.weather_trends)}
        Risk Alerts: {'; '.join(analysis.risk_alerts)}
        
        High Priority Insights:
        {self._format_insights(high_priority_insights)}
        
        All Insights Summary:
        - Total insights: {len(analysis.insights)}
        - Critical/High priority: {len(high_priority_insights)}
        - Categories: {', '.join(set(i.category for i in analysis.insights))}
        """
    
    def _format_insights(self, insights: List[WeatherInsight]) -> str:
        """Format insights for AI processing"""
        if not insights:
            return "No high-priority insights"
        
        formatted = []
        for insight in insights[:5]:  # Limit to top 5
            formatted.append(f"- {insight.title}: {insight.description} (Confidence: {insight.confidence:.1%})")
        
        return '\n'.join(formatted)
    
    def _extract_recommendations(self, ai_response: str, location: str) -> List[Recommendation]:
        """Extract structured recommendations from AI response"""
        recommendations = []
        current_section = None
        current_audience = "general_public"
        
        lines = ai_response.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Detect sections
            if 'IMMEDIATE ACTIONS' in line:
                current_section = 'immediate'
                current_audience = 'general_public'
            elif 'FARMING RECOMMENDATIONS' in line:
                current_section = 'farming'
                current_audience = 'farmers'
            elif 'DISASTER PREPAREDNESS' in line:
                current_section = 'disaster'
                current_audience = 'officials'
            elif 'PLANNING ADVICE' in line:
                current_section = 'planning'
                current_audience = 'general_public'
            elif 'MONITORING ALERTS' in line:
                current_section = 'monitoring'
                current_audience = 'general_public'
            elif line.startswith('- ') and current_section:
                # Parse recommendation
                text = line[2:]
                
                rec = Recommendation(
                    target_audience=current_audience,
                    action_type=current_section,
                    priority=self._determine_priority(text, current_section),
                    title=self._extract_title(text),
                    action=text,
                    reasoning=self._extract_reasoning(text),
                    timing=self._determine_timing(text, current_section),
                    resources_needed=self._identify_resources(text)
                )
                recommendations.append(rec)
        
        return recommendations
    
    async def _extract_recommendations_with_ai(self, ai_response: str, location: str, audience: str) -> List[Recommendation]:
        """Extract structured recommendations from AI response using AI parsing"""
        
        # Use AI to extract structured recommendations from the response
        extraction_prompt = ChatPromptTemplate.from_template("""
        You are an expert at extracting actionable recommendations from weather advisory text.
        
        Analyze the following weather advisory response and extract specific recommendations in JSON format:
        
        {ai_response}
        
        Extract recommendations and classify them by:
        - target_audience: farmers, officials, general_public
        - action_type: immediate, preparation, planning, monitoring
        - priority: critical, high, medium, low
        - timing: now, within_24h, this_week, next_week
        
        For each recommendation, extract:
        - title: brief 5-8 word action summary
        - action: the specific action to take
        - reasoning: why this action is recommended
        - resources_needed: what's needed (array of strings)
        
        Return ONLY a JSON array with this exact structure:
        [
          {{
            "target_audience": "farmers|officials|general_public",
            "action_type": "immediate|preparation|planning|monitoring",
            "priority": "critical|high|medium|low",
            "title": "Brief action title",
            "action": "Specific action to take",
            "reasoning": "Why this action is recommended",
            "timing": "now|within_24h|this_week|next_week",
            "resources_needed": ["resource1", "resource2"]
          }}
        ]
        
        Extract 5-15 actionable recommendations relevant to {audience}. Focus on practical, specific actions.
        """)
        
        try:
            messages = extraction_prompt.format_messages(
                ai_response=ai_response,
                audience=audience
            )
            response = await self.llm.ainvoke(messages)
            
            # Parse JSON response
            import json
            recommendations_data = json.loads(response.content.strip())
            
            # Convert to Recommendation objects
            recommendations = []
            for item in recommendations_data:
                recommendation = Recommendation(
                    target_audience=item.get('target_audience', 'general_public'),
                    action_type=item.get('action_type', 'planning'),
                    priority=item.get('priority', 'medium'),
                    title=item.get('title', 'Weather action'),
                    action=item.get('action', ''),
                    reasoning=item.get('reasoning', 'Based on weather conditions'),
                    timing=item.get('timing', 'within_24h'),
                    resources_needed=item.get('resources_needed', [])
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            print(f"🚨 AI recommendation extraction failed: {e}")
            # Fallback to original parsing method
            return self._extract_recommendations_fallback(ai_response, location)
    
    def _extract_recommendations_fallback(self, ai_response: str, location: str) -> List[Recommendation]:
        """Fallback method using original parsing logic"""
        return self._extract_recommendations(ai_response, location)
    
    def _determine_priority(self, text: str, section: str) -> str:
        """Determine priority level"""
        text_lower = text.lower()
        
        if section == 'immediate':
            return 'critical'
        elif any(word in text_lower for word in ['urgent', 'critical', 'danger', 'warning']):
            return 'critical'
        elif any(word in text_lower for word in ['important', 'should', 'risk', 'protect']):
            return 'high'
        elif any(word in text_lower for word in ['consider', 'plan', 'prepare']):
            return 'medium'
        else:
            return 'low'
    
    def _extract_title(self, text: str) -> str:
        """Extract brief title from recommendation text"""
        # Take first sentence or first 60 characters
        if '. ' in text:
            return text.split('. ')[0]
        elif len(text) > 60:
            return text[:57] + "..."
        else:
            return text
    
    def _extract_reasoning(self, text: str) -> str:
        """Extract reasoning from text"""
        # Look for explanatory phrases
        reasoning_indicators = ['because', 'due to', 'as', 'since', 'to prevent', 'to avoid']
        
        for indicator in reasoning_indicators:
            if indicator in text.lower():
                parts = text.lower().split(indicator, 1)
                if len(parts) > 1:
                    return f"Because {parts[1].strip()}"
        
        return "Based on current weather conditions and forecast"
    
    def _determine_timing(self, text: str, section: str) -> str:
        """Determine when to act"""
        text_lower = text.lower()
        
        if section == 'immediate':
            return 'now'
        elif any(word in text_lower for word in ['immediately', 'now', 'today', 'asap']):
            return 'now'
        elif any(word in text_lower for word in ['tomorrow', '24 hour', 'within day']):
            return 'within_24h'
        elif any(word in text_lower for word in ['this week', '3 day', 'few days']):
            return 'this_week'
        elif section == 'planning':
            return 'this_week'
        else:
            return 'within_24h'
    
    def _identify_resources(self, text: str) -> List[str]:
        """Identify resources needed from text"""
        resources = []
        text_lower = text.lower()
        
        # Common resources mentioned
        resource_keywords = {
            'water': ['irrigate', 'water', 'irrigation'],
            'equipment': ['equipment', 'tools', 'machinery'],
            'materials': ['materials', 'supplies', 'cover', 'tarp'],
            'help': ['assistance', 'help', 'support', 'coordination'],
            'information': ['monitor', 'check', 'watch', 'information'],
            'transportation': ['transport', 'vehicle', 'move', 'evacuate']
        }
        
        for resource, keywords in resource_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                resources.append(resource)
        
        return resources[:3]  # Limit to 3 resources
    
    def _create_priority_summary(self, recommendations: List[Recommendation]) -> str:
        """Create a priority summary of recommendations"""
        critical = len([r for r in recommendations if r.priority == 'critical'])
        high = len([r for r in recommendations if r.priority == 'high'])
        immediate = len([r for r in recommendations if r.timing == 'now'])
        
        summary = f"Priority Overview: {critical} critical actions, {high} high-priority recommendations, {immediate} requiring immediate attention."
        
        if critical > 0:
            summary += " Focus on critical actions first."
        elif high > 0:
            summary += " Address high-priority items within 24 hours."
        else:
            summary += " No urgent actions required - focus on planning and preparation."
        
        return summary
    
    def _create_action_checklist(self, recommendations: List[Recommendation]) -> List[str]:
        """Create a simple action checklist"""
        checklist = []
        
        # Sort by priority and timing
        sorted_recs = sorted(
            recommendations,
            key=lambda r: (
                {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}[r.priority],
                {'now': 0, 'within_24h': 1, 'this_week': 2, 'next_week': 3}[r.timing]
            )
        )
        
        for i, rec in enumerate(sorted_recs[:10], 1):  # Top 10 actions
            timing_label = {
                'now': '🔴 NOW',
                'within_24h': '🟡 24H',
                'this_week': '🟢 WEEK',
                'next_week': '🔵 LATER'
            }.get(rec.timing, '⚪ PLAN')
            
            checklist.append(f"{timing_label}: {rec.title}")
        
        return checklist
    
    def _generate_contact_suggestions(self, risk_alerts: List[str]) -> List[str]:
        """Generate contact suggestions based on risks"""
        contacts = []
        
        if any('storm' in alert.lower() or 'wind' in alert.lower() for alert in risk_alerts):
            contacts.append("Local emergency management office for storm preparations")
        
        if any('flood' in alert.lower() or 'rain' in alert.lower() for alert in risk_alerts):
            contacts.append("Agricultural extension office for flood mitigation advice")
        
        if any('heat' in alert.lower() or 'drought' in alert.lower() for alert in risk_alerts):
            contacts.append("Local health department for heat safety information")
        
        if any('frost' in alert.lower() or 'cold' in alert.lower() for alert in risk_alerts):
            contacts.append("Agricultural extension for crop protection guidance")
        
        # Always include general contacts
        contacts.extend([
            "Local weather service for updated forecasts",
            "Agricultural extension office for farming guidance",
            "Community emergency coordinator for disaster preparation"
        ])
        
        return list(set(contacts))  # Remove duplicates
    
    async def _create_audience_prompt(self, audience: str) -> ChatPromptTemplate:
        """Create AI-generated audience-specific prompt for advice generation"""
        
        # Check cache first to avoid regenerating the same prompt
        if audience in self._audience_prompt_cache:
            print(f"🔄 Using cached advice prompt for audience: {audience}")
            return self._audience_prompt_cache[audience]
        
        print(f"🤖 Generating AI-powered advice prompt for audience: {audience}")
        
        # Use AI to generate audience-specific advice prompt
        prompt_generator = ChatPromptTemplate.from_template("""
        You are an expert in creating specialized weather advisory prompts for different audiences.
        
        Create a comprehensive weather advisory prompt specifically tailored for: {audience}
        
        Your task is to design a prompt that will guide a weather advisor to provide the most relevant and actionable recommendations for this specific audience.
        
        Consider:
        1. What are the main responsibilities and concerns of {audience}?
        2. What weather-related decisions and actions do they need to take?
        3. What terminology and communication style works best for them?
        4. What are their primary assets, operations, or activities that weather affects?
        5. What format and structure would be most useful for their decision-making?
        6. What timeframes are most critical for their planning?
        
        Generate a detailed prompt that includes:
        - Role definition appropriate for advising {audience}
        - Specific focus areas relevant to {audience}
        - Types of recommendations they need (immediate, short-term, planning)
        - Risk factors and safety considerations specific to their context
        - Communication style and language complexity
        - Output format structure that serves their needs
        - Emphasis on actionable, practical guidance
        
        Return ONLY the weather advisory prompt (not meta-commentary). The prompt should start with:
        "You are a weather advisory specialist helping [audience]..."
        
        The prompt should include placeholders for {{data_analysis}} and {{forecast_analysis}} that will be filled with actual weather information.
        
        Make sure the prompt generates advice that is:
        - Highly specific to {audience} needs and context
        - Actionable with clear steps and timing
        - Appropriate for their level of weather expertise
        - Focused on their primary concerns and operations
        """)
        
        # Generate the audience-specific prompt
        messages = prompt_generator.format_messages(audience=audience)
        response = await self.llm.ainvoke(messages)
        
        # Extract the generated prompt text
        generated_prompt = response.content.strip()
        
        # Create the ChatPromptTemplate and cache it
        audience_prompt = ChatPromptTemplate.from_template(generated_prompt)
        self._audience_prompt_cache[audience] = audience_prompt
        
        print(f"✅ Generated and cached advice prompt for audience: {audience}")
        return audience_prompt