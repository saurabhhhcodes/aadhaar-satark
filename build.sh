#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🚀 Starting Build Process..."

# 1. Install Python Dependencies
echo "🐍 Installing Python Dependencies..."
pip install -r backend/requirements.txt

# 2. Build Frontend
echo "⚛️ Building Frontend..."
cd frontend
npm install
npm run build
cd ..

# 3. Verification
if [ -d "frontend/out" ]; then
    echo "✅ Frontend Build Successful (out directory exists)"
else
    echo "❌ Frontend Build Failed!"
    exit 1
fi

echo "🎉 Build Complete!"
