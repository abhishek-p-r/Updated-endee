#!/usr/bin/env python3
"""
Setup Verification Script

Checks if all components are properly configured and ready to use.
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from typing import Tuple


class Colors:
    """ANSI color codes."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")


# ============================================================================
# Verification Functions
# ============================================================================

def check_python_version() -> bool:
    """Check Python version."""
    print_header("Python Version")
    
    version = sys.version_info
    python_version = f"{version.major}.{version.minor}.{version.micro}"
    
    print(f"Python version: {python_version}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print_error("Python 3.9+ required")
        return False
    
    print_success("Python version OK")
    return True


def check_dependencies() -> bool:
    """Check if required packages are installed."""
    print_header("Python Dependencies")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'streamlit',
        'openai',
        'pydantic',
        'numpy',
        'pandas',
        'httpx',
        'PyPDF2'
    ]
    
    all_ok = True
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package}")
        except ImportError:
            print_error(f"{package} - NOT INSTALLED")
            all_ok = False
    
    if not all_ok:
        print_warning("Install missing packages: pip install -r requirements.txt")
    
    return all_ok


def check_environment_variables() -> bool:
    """Check required environment variables."""
    print_header("Environment Variables")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if openai_key:
        masked_key = openai_key[:10] + "..." + openai_key[-5:]
        print_success(f"OPENAI_API_KEY set ({masked_key})")
    else:
        print_error("OPENAI_API_KEY not set")
        print_info("Get key from: https://platform.openai.com/api-keys")
        return False
    
    return True


async def check_endee_server() -> bool:
    """Check if Endee server is running."""
    print_header("Endee Vector Database")
    
    try:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8000/health",
                timeout=5
            )
            
            if response.status_code == 200:
                print_success("Endee server is running on localhost:8000")
                return True
    except Exception as e:
        print_error(f"Cannot connect to Endee server")
        print_info("Start Endee with:")
        print_info("  docker run -p 8000:8000 endeeio/endee:latest")
        return False


async def check_openai_connection() -> bool:
    """Check OpenAI API connection."""
    print_header("OpenAI API")
    
    try:
        from openai import AsyncOpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            print_error("OPENAI_API_KEY not set")
            return False
        
        client = AsyncOpenAI(api_key=api_key)
        
        # Try a simple API call
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input="test"
        )
        
        print_success("OpenAI API connection OK")
        print_info(f"Embedding dimension: {len(response.data[0].embedding)}")
        
        return True
    
    except Exception as e:
        print_error(f"OpenAI API error: {str(e)}")
        
        if "Invalid API Key" in str(e):
            print_info("Check your OPENAI_API_KEY")
        elif "rate_limit" in str(e):
            print_warning("Rate limit exceeded, wait a moment")
        
        return False


def check_project_structure() -> bool:
    """Check if project structure is correct."""
    print_header("Project Structure")
    
    required_dirs = [
        'backend',
        'frontend',
        'scripts',
        'notebooks'
    ]
    
    required_files = [
        'backend/app.py',
        'backend/endee_vector_db.py',
        'backend/openai_client.py',
        'backend/rag_system.py',
        'frontend/app.py',
        'requirements.txt',
        '.env.example'
    ]
    
    all_ok = True
    
    for dir_name in required_dirs:
        if Path(dir_name).is_dir():
            print_success(f"Directory: {dir_name}")
        else:
            print_error(f"Directory missing: {dir_name}")
            all_ok = False
    
    for file_name in required_files:
        if Path(file_name).is_file():
            print_success(f"File: {file_name}")
        else:
            print_error(f"File missing: {file_name}")
            all_ok = False
    
    return all_ok


def check_ports() -> bool:
    """Check if required ports are available."""
    print_header("Port Availability")
    
    ports = {
        "8000": "API Server",
        "8501": "Streamlit UI"
    }
    
    all_ok = True
    
    for port, service in ports.items():
        try:
            result = subprocess.run(
                f"lsof -i :{port}",
                shell=True,
                capture_output=True,
                timeout=2
            )
            
            if result.returncode == 0:
                print_warning(f"Port {port} ({service}) - IN USE")
                all_ok = False
            else:
                print_success(f"Port {port} ({service}) - Available")
        except:
            print_success(f"Port {port} ({service}) - Available")
    
    return all_ok


# ============================================================================
# Main Verification
# ============================================================================

async def main():
    """Run all verifications."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "ENDEE RAG SYSTEM - SETUP VERIFICATION".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    results = {}
    
    # Synchronous checks
    results['Python Version'] = check_python_version()
    results['Dependencies'] = check_dependencies()
    results['Environment Variables'] = check_environment_variables()
    results['Project Structure'] = check_project_structure()
    results['Port Availability'] = check_ports()
    
    # Async checks
    results['Endee Server'] = await check_endee_server()
    results['OpenAI Connection'] = await check_openai_connection()
    
    # Summary
    print_header("Verification Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check_name, result in results.items():
        if result:
            print_success(check_name)
        else:
            print_error(check_name)
    
    print(f"\n{Colors.BOLD}Result: {passed}/{total} checks passed{Colors.ENDC}\n")
    
    if passed == total:
        print(Colors.GREEN + Colors.BOLD)
        print("✓ All checks passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Start the API server:")
        print("   python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000")
        print("\n2. Start the web interface:")
        print("   streamlit run frontend/app.py")
        print("\n3. Try the demo:")
        print("   python scripts/demo.py")
        print(Colors.ENDC)
        return 0
    
    elif passed >= total * 0.7:
        print(Colors.YELLOW + Colors.BOLD)
        print("⚠ Some checks failed. Review the errors above.")
        print(Colors.ENDC)
        return 1
    
    else:
        print(Colors.RED + Colors.BOLD)
        print("✗ Multiple critical issues found. Please fix them.")
        print(Colors.ENDC)
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
