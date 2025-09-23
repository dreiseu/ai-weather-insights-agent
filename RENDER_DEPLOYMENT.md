# Vercel + Render Deployment Guide

Step-by-step deployment of AI Weather Insights Agent using Vercel (frontend) and Render (backend).

## 🚀 Backend Deployment (Render)

### Step 1: Prepare for Render

1. **Ensure your code is pushed to GitHub**:
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push
   ```

### Step 2: Deploy to Render

1. **Go to [Render.com](https://render.com)** and sign up/login
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service**:
   - **Name**: `weather-insights-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3: Add Environment Variables

In the Render dashboard, add these environment variables:

```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Optional Configuration
TZ=Asia/Manila
ENVIRONMENT=production
LOG_LEVEL=INFO
QDRANT_URL=http://localhost:6333
```

### Step 4: Deploy Qdrant (Vector Database)

**Option A: Separate Render Service (Recommended)**
1. Click "New +" → "Web Service"
2. Select "Deploy an existing image from a registry"
3. **Image URL**: `qdrant/qdrant:latest`
4. **Name**: `weather-insights-qdrant`
5. **Port**: `6333`

**Option B: Use Qdrant Cloud**
1. Sign up at [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create a cluster
3. Update `QDRANT_URL` in backend environment variables

### Step 5: Update Backend Qdrant URL

If using separate Qdrant service on Render:
```bash
QDRANT_URL=https://weather-insights-qdrant.onrender.com
```

## 🌐 Frontend Deployment (Vercel)

### Step 1: Deploy to Vercel

1. **Go to [Vercel.com](https://vercel.com)** and sign up/login
2. **Click "New Project"**
3. **Import your GitHub repository**
4. **Configure the project**:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### Step 2: Add Environment Variables

In Vercel dashboard → Settings → Environment Variables:

```bash
VITE_API_BASE_URL=https://your-backend-url.onrender.com/api
```

Replace `your-backend-url` with your actual Render backend URL.

### Step 3: Deploy

Click "Deploy" and wait for the build to complete.

## 🔗 Linking Frontend and Backend

### Step 1: Get Backend URL

After Render deployment completes, copy your backend URL:
- Format: `https://weather-insights-backend.onrender.com`

### Step 2: Update Frontend Environment

1. Go to Vercel dashboard → Your project → Settings → Environment Variables
2. Update `VITE_API_BASE_URL`:
   ```bash
   VITE_API_BASE_URL=https://weather-insights-backend.onrender.com/api
   ```

### Step 3: Redeploy Frontend

1. Go to Vercel dashboard → Deployments
2. Click "Redeploy" on the latest deployment

## ✅ Testing Deployment

### Test Backend Health

```bash
curl https://your-backend-url.onrender.com/health
```

Expected response:
```json
{
  "status": "operational",
  "version": "1.0.0",
  "timestamp": "2024-01-XX...",
  "uptime": "X:XX:XX"
}
```

### Test Full Workflow

```bash
curl -X POST "https://your-backend-url.onrender.com/api/weather/insights" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Manila, PH",
    "audience": "farmers"
  }'
```

### Test Frontend

Visit your Vercel URL and test the weather insights functionality.

## 💰 Cost Breakdown

### Render
- **Web Services**: Free tier available (limited hours)
- **Paid**: $7/month for always-on services

### Vercel
- **Frontend**: Free tier (unlimited personal projects)
- **Bandwidth**: 100GB/month free

### Qdrant
- **Self-hosted on Render**: Included in service cost
- **Qdrant Cloud**: Free tier available, $25/month for production

## 🐛 Troubleshooting

### Common Issues

1. **Backend not starting**:
   - Check environment variables are set correctly
   - Verify build logs in Render dashboard

2. **Frontend can't connect to backend**:
   - Verify `VITE_API_BASE_URL` is correct
   - Check CORS settings in backend

3. **Qdrant connection failed**:
   - Ensure Qdrant service is running
   - Check `QDRANT_URL` environment variable

4. **API timeouts**:
   - Render free tier has cold starts (services sleep after 15 min)
   - Consider upgrading to paid tier for production

### Health Check URLs

- **Backend**: `https://your-backend-url.onrender.com/health`
- **Qdrant**: `https://your-qdrant-url.onrender.com/health`
- **Frontend**: Your Vercel URL

## 🚀 Go Live!

Once both services are deployed and connected:

1. **Frontend URL**: `https://your-project.vercel.app`
2. **Backend URL**: `https://your-backend.onrender.com`

Your AI Weather Insights Agent is now live and accessible worldwide! 🌍

## 📞 Support

If you encounter issues:
- Check Render build logs
- Verify Vercel function logs
- Test API endpoints directly
- Ensure environment variables are correctly set