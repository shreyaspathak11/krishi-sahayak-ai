#!/usr/bin/env python3
"""
Startup script for Krishi Sahayak AI
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main startup function"""
    
    # Check for required environment variables
    required_env_vars = ["GROQ_API_KEY", "OPENWEATHERMAP_API_KEY"]
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file or set these environment variables.")
        print("See .env.example for reference.")
        sys.exit(1)
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    environment = os.getenv("ENVIRONMENT", "development")
    
    print("🌾 Starting Krishi Sahayak AI...")
    print(f"   Environment: {environment}")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=environment == "development",
        log_level="info"
    )

if __name__ == "__main__":
    main()
