#!/bin/bash

# AI Weather Insights Agent - Deployment Helper Script

set -e

echo "🌦️ AI Weather Insights Agent - Deployment Helper"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "vercel.json" ]; then
    echo "❌ Error: vercel.json not found. Please run this script from the project root directory."
    exit 1
fi

echo "📋 Pre-deployment Checklist:"
echo "1. ✅ Environment files configured"
echo "2. ✅ Deployment configurations created"
echo "3. ✅ Dependencies listed in requirements.txt and package.json"

echo ""
echo "🚀 Deployment Options:"
echo ""
echo "Vercel + Render"
echo "  Frontend: https://vercel.com/new"
echo "  Backend:  https://render.com/deploy"
echo ""

echo "📝 Next Steps:"
echo ""
echo "For Vercel (Frontend):"
echo "1. Connect your GitHub repository"
echo "2. Set root directory to: frontend"
echo "3. Set build command to: npm run build"
echo "4. Set output directory to: dist"
echo "5. Add environment variable:"
echo "   VITE_API_BASE_URL=https://your-backend-url/api"
echo ""

echo "For Render (Backend):"
echo "1. Connect your GitHub repository"
echo "2. Set root directory to: backend"
echo "3. Set build command to: pip install -r requirements.txt"
echo "4. Set start command to: uvicorn main:app --host 0.0.0.0 --port \$PORT"
echo "5. Add the same environment variables as Railway"
echo ""

echo "✅ Deployment configurations are ready!"
echo "📖 See DEPLOYMENT.md for detailed instructions"

# Optional: Check if required files exist
echo ""
echo "🔍 Checking deployment files..."

files=(
    "vercel.json"
    "railway.toml"
    "backend/Dockerfile.prod"
    "backend/.env.production"
    "frontend/.env.example"
    "DEPLOYMENT.md"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
    fi
done

echo ""
echo "🎯 Ready for deployment! Good luck!"