#!/bin/bash

echo "🐳 Building Krishi Sahayak Docker image..."
docker build -t krishi-sahayak-ai .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    echo ""
    echo "🚀 To run the application:"
    echo "Production: docker-compose up"
    echo "Development: docker-compose --profile dev up krishi-sahayak-ai-dev"
    echo ""
    echo "📝 Direct docker run:"
    echo "docker run -p 8000:8000 --env-file .env krishi-sahayak-ai"
else
    echo "❌ Docker build failed!"
    exit 1
fi
