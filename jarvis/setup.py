"""
Setup script for JARVIS
Installs dependencies and initializes required databases
"""

import os
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("JARVIS requires Python 3.8 or higher")
        sys.exit(1)

def install_system_dependencies():
    """Install required system packages"""
    try:
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run([
            "sudo", "apt-get", "install", "-y",
            "redis-server",
            "postgresql",
            "postgresql-contrib",
            "python3-dev",
            "build-essential"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install system dependencies: {e}")
        sys.exit(1)

def install_python_dependencies():
    """Install Python packages"""
    requirements_path = Path(__file__).parent / "requirements.txt"
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "-r", str(requirements_path)
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Python dependencies: {e}")
        sys.exit(1)

def setup_postgresql():
    """Initialize PostgreSQL database"""
    try:
        # Start PostgreSQL service
        subprocess.run(["sudo", "service", "postgresql", "start"], check=True)
        
        # Create database and user
        subprocess.run([
            "sudo", "-u", "postgres", "psql",
            "-c", "CREATE DATABASE jarvis_memory;"
        ], check=True)
        
        subprocess.run([
            "sudo", "-u", "postgres", "psql",
            "-c", "CREATE USER jarvis WITH PASSWORD 'jarvis_password';"
        ], check=True)
        
        subprocess.run([
            "sudo", "-u", "postgres", "psql",
            "-c", "GRANT ALL PRIVILEGES ON DATABASE jarvis_memory TO jarvis;"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to setup PostgreSQL: {e}")
        sys.exit(1)

def setup_redis():
    """Initialize Redis"""
    try:
        # Start Redis service
        subprocess.run(["sudo", "service", "redis-server", "start"], check=True)
        
        # Test Redis connection
        subprocess.run(["redis-cli", "ping"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to setup Redis: {e}")
        sys.exit(1)

def create_env_file():
    """Create .env file with default configuration"""
    env_path = Path(__file__).parent / ".env"
    
    env_content = """
# JARVIS Environment Configuration

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
POSTGRES_DB=jarvis_memory
POSTGRES_USER=jarvis
POSTGRES_PASSWORD=jarvis_password
POSTGRES_HOST=localhost

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Logging
LOG_LEVEL=INFO
LOG_FILE=jarvis.log

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
    """.strip()
    
    with open(env_path, "w") as f:
        f.write(env_content)
    
    print("Created .env file. Please update with your actual configuration.")

def main():
    """Main setup function"""
    print("Setting up JARVIS...")
    
    # Check Python version
    check_python_version()
    print("✓ Python version check passed")
    
    # Install system dependencies
    print("Installing system dependencies...")
    install_system_dependencies()
    print("✓ System dependencies installed")
    
    # Install Python packages
    print("Installing Python packages...")
    install_python_dependencies()
    print("✓ Python packages installed")
    
    # Setup PostgreSQL
    print("Setting up PostgreSQL...")
    setup_postgresql()
    print("✓ PostgreSQL setup complete")
    
    # Setup Redis
    print("Setting up Redis...")
    setup_redis()
    print("✓ Redis setup complete")
    
    # Create .env file
    print("Creating environment configuration...")
    create_env_file()
    print("✓ Environment configuration created")
    
    print("\nJARVIS setup complete!")
    print("\nNext steps:")
    print("1. Update the .env file with your OpenAI API key")
    print("2. Review and adjust the configuration in config/config.yaml")
    print("3. Run 'python -m jarvis' to start the system")

if __name__ == "__main__":
    main()