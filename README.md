# AI Weather Insights Agent 🌦️

Transforms raw weather data into actionable insights for rural communities, farmers, and local officials using AI agents and RAG pipeline.

## 🎯 Problem Statement

Rural communities receive technical weather data that's hard to interpret without expertise. This leads to poor preparedness for agriculture, fishing, and disaster management.

## 💡 Solution

AI Weather Insights Agent that converts weather station data + forecasts into human-friendly, actionable recommendations through a multi-agent workflow:

- **Data Agent** → Cleans and validates weather readings
- **Forecast Agent** → Predicts short-term implications  
- **Advice Agent** → Outputs actionable recommendations

## 🏗️ Architecture

```
Frontend (React/Node.js) 
    ↓ HTTP API
Backend (FastAPI/Python)
    ↓ Multi-Agent Workflow (LangGraph)
    ├── OpenWeather API (weather data)
    ├── OpenAI API (LLM processing)
    └── Qdrant (RAG knowledge base)
```

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- Docker & Docker Compose
- OpenAI API key
- OpenWeather API key

### 1. Environment Setup

```bash
# Clone and navigate
git clone <repository>
cd weather_insights_agent

# Backend environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

### 2. Start with Docker

```bash
# Start Qdrant + Backend
docker-compose up -d

# Check services
docker-compose ps
```

### 3. Manual Setup (Development)

```bash
# Backend
cd backend
pip install -r requirements.txt

# Start Qdrant separately
docker run -p 6333:6333 qdrant/qdrant:v1.7.0

# Run backend
python main.py
```

## 🔧 API Endpoints

### Single Location Analysis
```bash
curl -X POST "http://localhost:8000/api/weather/insights" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Manila, PH",
    "audience": "farmers"
  }'
```

### Batch Analysis
```bash
curl -X POST "http://localhost:8000/api/weather/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "locations": ["Manila, PH", "Cebu, PH", "Davao, PH"],
    "audience": "officials"
  }'
```

### System Status
```bash
curl "http://localhost:8000/api/system/status"
```

## 🌍 Demo Use Cases

### For Farmers
```json
{
  "location": "Iloilo, PH",
  "audience": "farmers"
}
```
**Output**: Planting recommendations, irrigation timing, crop protection advice

### For Local Officials  
```json
{
  "location": "Tacloban, PH", 
  "audience": "officials"
}
```
**Output**: Disaster preparedness, community safety alerts, resource coordination

### For General Public
```json
{
  "location": "Baguio, PH",
  "audience": "general"
}
```
**Output**: Daily activity planning, safety precautions, travel advice

## 🧠 Agent Workflow

1. **Data Agent**: Validates weather data quality, detects anomalies
2. **Forecast Agent**: Analyzes 5-day forecast, identifies patterns & risks  
3. **Advice Agent**: Generates prioritized, actionable recommendations
4. **RAG System**: Provides relevant weather knowledge & best practices

## 📊 Example Output

```json
{
  "location": "Manila, PH",
  "current_weather": {
    "temperature": 32.5,
    "humidity": 78,
    "condition": "Thunderstorm approaching"
  },
  "recommendations": [
    {
      "priority": "critical", 
      "timing": "now",
      "title": "Secure outdoor equipment",
      "action": "Move livestock to sheltered areas due to approaching thunderstorm",
      "target_audience": "farmers"
    }
  ],
  "risk_alerts": [
    "STORM ALERT: Thunderstorms predicted - secure outdoor equipment"
  ]
}
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11, LangChain, LangGraph
- **AI/LLM**: OpenAI GPT-3.5-turbo  
- **Vector DB**: Qdrant (RAG pipeline)
- **Weather Data**: OpenWeather API
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons
- **Deployment**: Docker, Docker Compose

## 📈 Impact & Demo Value

- **For Farmers**: Reduces crop loss through smart decision timing
- **For Officials**: Improves disaster preparedness and response  
- **For Citizens**: Accessible weather briefings without technical jargon
- **Demonstrates**: How LLMs can translate complex data into life-saving knowledge

## 🚀 Production Deployment

### Quick Deploy Options

**Vercel + Render**
- Frontend: Deploy to [Vercel](https://vercel.com) (free tier)
- Backend: Deploy to [Render](https://render.com) (free tier available)

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

### Environment Variables for Production
```bash
# Frontend (Vercel)
VITE_API_BASE_URL=https://your-backend-url.onrender.com/api

# Backend (Render)
OPENAI_API_KEY=your_openai_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
TZ=Asia/Manila
PORT=8000
```

## 🚀 Development Roadmap

- [x] Backend API with multi-agent workflow
- [x] React frontend dashboard with interactive UI
- [x] AI-generated audience-specific prompts
- [x] Interactive action checklist with expandable details
- [x] Multi-agent coordination with LangGraph
- [x] Comprehensive data visualization suite
- [x] Timezone handling for Philippines (GMT+8)
- [x] Production deployment configuration
- [ ] Real-time weather monitoring
- [ ] Historical pattern learning
- [ ] Mobile app version

## 📝 Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...           # OpenAI API key
OPENWEATHER_API_KEY=...         # OpenWeather API key

# Optional  
QDRANT_URL=http://localhost:6333  # Vector database URL
ENVIRONMENT=development           # development/production
LOG_LEVEL=INFO                   # Logging level
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📜 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- OpenWeather for weather data API
- OpenAI for LLM capabilities  
- Qdrant for vector database
- Rural communities inspiring this solution