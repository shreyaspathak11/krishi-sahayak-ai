#!/usr/bin/env python3
"""
Startup script for Krishi Sahayak
"""

import os
import sys
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
load_dotenv()

def main():
    """Main startup function"""
    
    # Set UTF-8 encoding for console output
    import io
    import sys
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # Check for required environment variables
    required_env_vars = ["GROQ_API_KEY", "OPENWEATHERMAP_API_KEY"]
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("[ERROR] Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file or set these environment variables.")
        print("See .env.example for reference.")
        sys.exit(1)
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    environment = os.getenv("ENVIRONMENT", "development")
    
    # Render requires 127.0.0.1, Docker uses 0.0.0.0
    if environment == "production":
        host = "127.0.0.1"
    else:
        host = "0.0.0.0"
    
    print("[INFO] Starting Krishi Sahayak...")
    print(f"   Environment: {environment}")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    
    # Run the application
    try:
        # Use specific Uvicorn config to ensure it doesn't exit prematurely
        config = uvicorn.Config(
            "app.main:app",
            host=host,
            port=port,
            reload=False,  # Disable reload in production
            log_level="info",
            access_log=True,
            lifespan="auto"
        )
        server = uvicorn.Server(config)
        # This will block indefinitely
        import asyncio
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        print("[INFO] Server shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Server failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
