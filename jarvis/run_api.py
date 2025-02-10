"""
Script to run the JARVIS API server
"""

import uvicorn
import logging
import os
from pathlib import Path
import yaml

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Load configuration
    config_path = Path(__file__).parent / "config" / "config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Run API server
    uvicorn.run(
        "api:app",
        host=config["api"]["host"],
        port=config["api"]["port"],
        reload=True
    )

if __name__ == "__main__":
    main()