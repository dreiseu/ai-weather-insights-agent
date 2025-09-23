# Deployment Guide

This guide covers deploying the AI Weather Insights Agent to production.

## Architecture

- **Frontend**: React app deployed on Vercel
- **Backend**: FastAPI app deployed on Render
- **Database**: Qdrant vector database (containerized or managed service)

## Quick Deployment Options

### Vercel + Render (Recommended)

#### Frontend (Vercel)
1. **Connect Repository**:
   ```bash
   # Visit https://vercel.com and connect your GitHub repo
   # Root directory: frontend
   # Build command: npm run build
   # Output directory: dist
   ```

2. **Environment Variables**:
   ```
   VITE_API_BASE_URL=https://your-backend-url.onrender.com/api
   ```

#### Backend (Render)
1. **Create Web Service**:
   - Connect GitHub repo
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Environment Variables**:
   ```
   OPENAI_API_KEY=your_openai_api_key
   OPENWEATHER_API_KEY=your_openweather_api_key
   TZ=Asia/Manila
   QDRANT_URL=internal_qdrant_url
   ```

## Environment Variables Setup

### Required Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENWEATHER_API_KEY`: Your OpenWeather API key

### Optional Variables
- `QDRANT_URL`: Vector database URL (default: http://localhost:6333)
- `TZ`: Timezone (default: Asia/Manila)
- `LOG_LEVEL`: Logging level (default: INFO)

## Database Deployment

### Option A: Managed Qdrant Cloud
1. Sign up at [Qdrant Cloud](https://cloud.qdrant.io/)
2. Create a cluster
3. Update `QDRANT_URL` environment variable

### Option B: Self-hosted Qdrant
- Deploy Qdrant container alongside your backend
- Use docker-compose or container orchestration platform

## Post-Deployment

1. **Test the deployment**:
   ```bash
   curl https://your-backend-url/health
   ```

2. **Monitor logs** for any errors

3. **Update frontend API URL** in Vercel environment variables

## Troubleshooting

### Common Issues
- **CORS errors**: Ensure backend allows frontend domain in CORS settings
- **API timeouts**: Check if backend is properly deployed and responding
- **Environment variables**: Verify all required variables are set correctly

### Health Checks
- Backend health: `GET /health`
- API test: `POST /api/test-connection`
- Full workflow: `POST /api/weather/insights`

## Cost Estimates

- **Vercel**: Free tier available
- **Railway**: ~$5-20/month depending on usage
- **Render**: Free tier available, paid plans from $7/month
- **Qdrant Cloud**: Free tier available, paid plans from $25/month