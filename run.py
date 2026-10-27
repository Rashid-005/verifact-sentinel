import os
import sys
import uvicorn
from pathlib import Path

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

from backend.config import HOST, PORT

def main():
    print("=" * 65)
    print("🚀 Starting VeriFact Sentinel Server...")
    print("   Powered by NVIDIA Nemotron-70B on Nebius Token Factory")
    print("   & Tavily AI Search Real-time Grounding Engine")
    print(f"👉 Local Access URL: http://{HOST}:{PORT}")
    print("=" * 65)
    
    uvicorn.run("backend.app:app", host=HOST, port=PORT, reload=True)

if __name__ == "__main__":
    main()
