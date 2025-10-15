"""
Startup script for LLM Code Deployment API
Validates setup and starts the server
"""
import sys
import subprocess
from pathlib import Path

def main():
    """Run validation and start server"""
    print("\n🚀 Starting LLM Code Deployment API...\n")
    
    # Run validation
    print("Step 1: Validating setup...")
    result = subprocess.run([sys.executable, "validate_setup.py"], capture_output=False)
    
    if result.returncode != 0:
        print("\n❌ Setup validation failed. Please fix the issues above.")
        return 1
    
    print("\n" + "=" * 60)
    print("Step 2: Starting FastAPI server...")
    print("=" * 60)
    print("\n💡 Server will be available at: http://localhost:7860")
    print("💡 API documentation at: http://localhost:7860/docs")
    print("💡 Press Ctrl+C to stop the server\n")
    
    # Start the server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "src.main:app",
            "--host", "0.0.0.0",
            "--port", "7860",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
