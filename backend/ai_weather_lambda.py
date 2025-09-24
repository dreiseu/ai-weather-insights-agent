"""
AI Weather Lambda with OpenAI integration - simplified version
"""
import json
import os
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone, timedelta

# Setup timezone (GMT+8 for Philippines)
PHILIPPINE_TZ = timezone(timedelta(hours=8))

def call_openai_api(messages, model="gpt-3.5-turbo", max_tokens=500):
    """Call OpenAI API using urllib"""
    print(f"Starting OpenAI API call...")
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return None, "OpenAI API key not configured"

        # Prepare the request
        url = "https://api.openai.com/v1/chat/completions"

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        print(f"OpenAI request payload: {json.dumps(payload)}")

        # Validate messages format
        if not messages or not isinstance(messages, list):
            print(f"ERROR: Invalid messages format: {messages}")
            return None, "Invalid messages format"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        # Create request
        data = json.dumps(payload).encode('utf-8')
        request = urllib.request.Request(url, data=data, headers=headers, method='POST')

        # Make request
        print(f"Making OpenAI API request...")
        with urllib.request.urlopen(request, timeout=25) as response:
            if response.getcode() != 200:
                print(f"OpenAI API returned error code: {response.getcode()}")
                return None, f"OpenAI API error: {response.getcode()}"

            # Read the full response
            response_bytes = response.read()
            response_text = response_bytes.decode('utf-8')
            print(f"Response length: {len(response_text)}")

            # Don't log the full response as it breaks across lines
            # print(f"Raw OpenAI response text: '{response_text}'")

            if not response_text.strip():
                print("ERROR: OpenAI returned empty response!")
                return None, "OpenAI returned empty response"

            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")
                print(f"Failed to parse response of length {len(response_text)}")
                return None, f"JSON parsing failed: {str(e)}"
            print(f"OpenAI API call completed successfully")
            return result, None

    except Exception as e:
        return None, str(e)

def get_weather_data(location):
    """Get weather data from OpenWeather API using urllib"""
    try:
        api_key = os.environ.get('OPENWEATHER_API_KEY')
        if not api_key:
            return None, "OpenWeather API key not configured"

        # Get current weather
        location_encoded = urllib.parse.quote(location)
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={location_encoded}&appid={api_key}&units=metric"

        with urllib.request.urlopen(weather_url, timeout=10) as response:
            if response.getcode() != 200:
                return None, f"Weather API error: {response.getcode()}"
            weather_data = json.loads(response.read().decode('utf-8'))

        # Get forecast data
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={location_encoded}&appid={api_key}&units=metric"

        with urllib.request.urlopen(forecast_url, timeout=10) as response:
            if response.getcode() != 200:
                return weather_data, None  # Return at least current weather
            forecast_data = json.loads(response.read().decode('utf-8'))

        return {"current": weather_data, "forecast": forecast_data}, None

    except Exception as e:
        return None, str(e)

def create_audience_prompt(audience):
    """Create audience-specific prompt"""
    prompts = {
        "farmers": "You are an agricultural weather advisor. Focus on crop management, irrigation, livestock care, and farming operations.",
        "officials": "You are a municipal weather advisor. Focus on public safety, infrastructure, emergency preparedness, and community coordination.",
        "general": "You are a general weather advisor. Focus on daily activities, safety precautions, and practical recommendations."
    }
    return prompts.get(audience, prompts["general"])

def analyze_weather_with_ai(weather_data, audience="general"):
    """Analyze weather using OpenAI"""
    try:
        current = weather_data.get("current", {})
        forecast = weather_data.get("forecast", {})

        # Prepare weather summary
        temp = current.get('main', {}).get('temp', 0)
        humidity = current.get('main', {}).get('humidity', 0)
        condition = current.get('weather', [{}])[0].get('description', 'unknown')
        location = current.get('name', 'Unknown')

        # Get forecast summary
        forecast_items = forecast.get('list', [])[:8]  # Next 24 hours
        forecast_summary = []
        for item in forecast_items:
            forecast_summary.append({
                'temp': item.get('main', {}).get('temp', 0),
                'condition': item.get('weather', [{}])[0].get('description', ''),
                'time': item.get('dt_txt', '')
            })

        # Create AI prompt
        audience_context = create_audience_prompt(audience)

        messages = [
            {
                "role": "system",
                "content": f"{audience_context} Provide specific, actionable recommendations based on weather conditions. Focus on practical advice relevant to the target audience."
            },
            {
                "role": "user",
                "content": f"""
                Current weather in {location}:
                - Temperature: {temp}°C
                - Humidity: {humidity}%
                - Condition: {condition}

                24-hour forecast: {json.dumps(forecast_summary)}

                Target audience: {audience}

                Please provide:
                1. 3-5 specific, actionable recommendations
                2. Priority level for each (critical/high/medium/low)
                3. Timing (immediate/within 2 hours/today/this week)
                4. Brief explanation of why each recommendation is important

                Format as JSON with this structure:
                {{
                    "recommendations": [
                        {{
                            "title": "recommendation title",
                            "action": "specific action to take",
                            "priority": "critical|high|medium|low",
                            "timing": "immediate|within 2 hours|today|this week",
                            "reason": "brief explanation",
                            "target_audience": "{audience}"
                        }}
                    ],
                    "risk_alerts": ["alert1", "alert2"],
                    "summary": "overall weather impact summary"
                }}
                """
            }
        ]

        # Call OpenAI
        print(f"Calling OpenAI API with {len(messages)} messages")
        ai_response, error = call_openai_api(messages)

        if error:
            print(f"OpenAI API error: {error}")
            return create_fallback_response(current, audience), f"AI analysis unavailable: {error}"

        print(f"OpenAI API call successful: {type(ai_response)}")

        # Parse AI response
        ai_content = ai_response.get('choices', [{}])[0].get('message', {}).get('content', '')
        print(f"OpenAI raw response: {ai_content}")

        try:
            # Try to parse as JSON
            ai_analysis = json.loads(ai_content)
            print(f"Successfully parsed AI response: {ai_analysis}")
        except json.JSONDecodeError as e:
            # Log the parsing error details
            print(f"JSON parsing failed. Error: {str(e)}")
            print(f"Raw content that failed: {repr(ai_content)}")
            return create_fallback_response(current, audience), f"AI response parsing failed: {str(e)}"

        # Combine with weather data
        result = {
            "location": location,
            "analysis_time": datetime.now(PHILIPPINE_TZ).isoformat(),
            "current_weather": {
                "temperature": temp,
                "humidity": humidity,
                "condition": condition
            },
            "recommendations": ai_analysis.get("recommendations", []),
            "risk_alerts": ai_analysis.get("risk_alerts", []),
            "summary": ai_analysis.get("summary", ""),
            "audience": audience,
            "success": True,
            "ai_powered": True
        }

        return result, None

    except Exception as e:
        return create_fallback_response(current, audience), str(e)

def create_fallback_response(weather_data, audience):
    """Create basic response when AI is unavailable"""
    temp = weather_data.get('main', {}).get('temp', 0)
    humidity = weather_data.get('main', {}).get('humidity', 0)
    condition = weather_data.get('weather', [{}])[0].get('description', 'unknown')

    # Basic rules-based recommendations
    recommendations = []

    if temp > 35:
        recommendations.append({
            "title": "High Temperature Alert",
            "action": "Stay hydrated and avoid prolonged sun exposure" if audience == "general" else "Provide shade for livestock and increase irrigation",
            "priority": "critical",
            "timing": "immediate",
            "reason": "Extreme heat can cause health issues",
            "target_audience": audience
        })

    return {
        "location": weather_data.get('name', 'Unknown'),
        "analysis_time": datetime.now(PHILIPPINE_TZ).isoformat(),
        "current_weather": {
            "temperature": temp,
            "humidity": humidity,
            "condition": condition
        },
        "recommendations": recommendations,
        "risk_alerts": [rec["title"] for rec in recommendations if rec["priority"] in ["critical", "high"]],
        "summary": f"Basic weather analysis for {weather_data.get('name', 'your location')}",
        "audience": audience,
        "success": True,
        "ai_powered": False
    }

def lambda_handler(event, context):
    """Lambda handler with full AI weather functionality"""

    # Add debug logging
    print(f"Lambda event: {json.dumps(event)}")

    method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')

    # CORS headers - Enhanced for frontend compatibility
    cors_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Accept, Origin',
        'Access-Control-Max-Age': '3600'
    }

    try:
        # Handle OPTIONS (CORS preflight) - for ANY path
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': ''
            }

        # Health endpoint
        if path == '/health':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'status': 'operational',
                    'version': '1.0.0',
                    'timestamp': datetime.now(PHILIPPINE_TZ).isoformat(),
                    'message': 'AI Weather Lambda backend is working!',
                    'features': ['weather_data', 'ai_insights', 'openai_integration', 'audience_targeting']
                })
            }

        # Weather insights endpoint - FULL AI VERSION
        elif path == '/weather/insights' and method == 'POST':
            try:
                # Safely parse request body
                body = {}
                if event.get('body'):
                    try:
                        body = json.loads(event.get('body'))
                    except json.JSONDecodeError:
                        return {
                            'statusCode': 400,
                            'headers': cors_headers,
                            'body': json.dumps({
                                'success': False,
                                'error': 'Invalid JSON in request body'
                            })
                        }

                location = body.get('location', 'Manila, PH')
                audience = body.get('audience', 'general')

                # Get weather data
                weather_data, error = get_weather_data(location)
                if error:
                    return {
                        'statusCode': 400,
                        'headers': cors_headers,
                        'body': json.dumps({
                            'success': False,
                            'error': error
                        })
                    }

                # Analyze with AI
                analysis, ai_error = analyze_weather_with_ai(weather_data, audience)

                if ai_error:
                    analysis['ai_error'] = ai_error

                response = {
                    'statusCode': 200,
                    'headers': cors_headers,
                    'body': json.dumps(analysis)
                }
                print(f"Returning successful response: {response}")
                return response

            except Exception as e:
                # Log the full error for debugging
                print(f"Weather insights error: {str(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                return {
                    'statusCode': 500,
                    'headers': cors_headers,
                    'body': json.dumps({
                        'success': False,
                        'error': f'Weather insights error: {str(e)}',
                        'timestamp': datetime.now(PHILIPPINE_TZ).isoformat()
                    })
                }

        # System status endpoint
        elif path == '/system/status':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'weather_api': 'operational' if os.environ.get('OPENWEATHER_API_KEY') else 'missing_key',
                    'openai_api': 'operational' if os.environ.get('OPENAI_API_KEY') else 'missing_key',
                    'backend': 'operational',
                    'timestamp': datetime.now(PHILIPPINE_TZ).isoformat(),
                    'environment': 'lambda',
                    'ai_features': 'enabled'
                })
            }

        # Test connection endpoint
        elif path == '/api/test-connection' and method == 'POST':
            try:
                body = json.loads(event.get('body', '{}')) if event.get('body') else {}
            except:
                body = {}

            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'status': 'success',
                    'message': 'AI Weather Lambda received your request!',
                    'received_data': body,
                    'timestamp': datetime.now(PHILIPPINE_TZ).isoformat(),
                    'ai_features': 'enabled'
                })
            }

        # Not found
        else:
            return {
                'statusCode': 404,
                'headers': cors_headers,
                'body': json.dumps({
                    'error': 'Not Found',
                    'path': path,
                    'method': method
                })
            }

    except Exception as e:
        # Global error handler
        print(f"Global Lambda error: {str(e)}")
        import traceback
        print(f"Global Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e),
                'timestamp': datetime.now(PHILIPPINE_TZ).isoformat()
            })
        }