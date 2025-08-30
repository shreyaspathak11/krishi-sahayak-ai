@echo off
echo 🐳 Building Krishi Sahayak Docker image...
docker build -t krishi-sahayak-ai .

if %errorlevel% equ 0 (
    echo ✅ Docker image built successfully!
    echo.
    echo 🚀 To run the application:
    echo Production: docker-compose up
    echo Development: docker-compose --profile dev up krishi-sahayak-ai-dev
    echo.
    echo 📝 Direct docker run:
    echo docker run -p 8000:8000 --env-file .env krishi-sahayak-ai
) else (
    echo ❌ Docker build failed!
    exit /b 1
)
