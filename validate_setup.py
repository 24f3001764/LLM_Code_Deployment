"""
Validate environment setup for LLM Code Deployment API
Run this before starting the server to ensure everything is configured correctly
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def check_env_var(name, required=True):
    """Check if environment variable is set"""
    value = os.getenv(name)
    if value:
        # Mask sensitive values
        if any(keyword in name.lower() for keyword in ['secret', 'key', 'token', 'password']):
            masked = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '*' * len(value)
            print(f"  ✅ {name}: {masked}")
        else:
            print(f"  ✅ {name}: {value}")
        return True
    else:
        if required:
            print(f"  ❌ {name}: NOT SET (required)")
            return False
        else:
            print(f"  ⚠️  {name}: NOT SET (optional)")
            return True

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.10+)")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'openai',
        'httpx',
        'github',
        'aiofiles',
        'dotenv'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (not installed)")
            all_installed = False
    
    return all_installed

def check_directories():
    """Check if required directories exist"""
    dirs = ['src', 'test']
    all_exist = True
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  ❌ {dir_name}/ (missing)")
            all_exist = False
    
    return all_exist

def check_api_keys():
    """Validate API keys format"""
    warnings = []
    
    # Check OpenAI API key format (warning only for non-standard keys like aipipe.org)
    openai_key = os.getenv('OPENAI_API_KEY', '')
    if openai_key:
        if not openai_key.startswith('sk-'):
            warnings.append("OpenAI API key should start with 'sk-' (unless using alternative provider like aipipe.org)")
    
    # Check GitHub token format
    github_token = os.getenv('GITHUB_TOKEN', '')
    if github_token:
        if not (github_token.startswith('ghp_') or github_token.startswith('gho_') or github_token.startswith('ghs_')):
            warnings.append("GitHub token should start with 'ghp_', 'gho_', or 'ghs_'")
    
    if warnings:
        for warning in warnings:
            print(f"  ⚠️  {warning}")
    
    # Always return True since these are just warnings
    return True

def test_github_connection():
    """Test GitHub API connection"""
    try:
        from github import Github, Auth
        token = os.getenv('GITHUB_TOKEN')
        username = os.getenv('GITHUB_USERNAME')
        
        if not token or not username:
            print("  ⚠️  Cannot test - credentials not set")
            return False
        
        # Use new Auth method to avoid deprecation warning
        auth = Auth.Token(token)
        g = Github(auth=auth)
        user = g.get_user()
        
        if user.login.lower() == username.lower():
            print(f"  ✅ Connected to GitHub as {user.login}")
            try:
                rate_limit = g.get_rate_limit()
                print(f"     Remaining API calls: {rate_limit.core.remaining}")
            except:
                # Skip rate limit check if it fails
                pass
            return True
        else:
            print(f"  ❌ GitHub username mismatch: {user.login} != {username}")
            return False
            
    except Exception as e:
        print(f"  ❌ GitHub connection failed: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connection"""
    try:
        from openai import OpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')  # ADD THIS LINE
        
        if not api_key:
            print("  ⚠️  Cannot test - API key not set")
            return False
        
        # Use custom base_url for alternative providers like aipipe.org
        client = OpenAI(api_key=api_key, base_url=base_url)  # UPDATE THIS LINE
        
        # Try to list models to verify the key works
        models = client.models.list()
        print(f"  ✅ Connected to OpenAI API")
        if base_url != 'https://api.openai.com/v1':  # ADD THESE LINES
            print(f"     Using custom endpoint: {base_url}")
        return True
            
    except Exception as e:
        print(f"  ❌ OpenAI connection failed: {e}")
        return False

def main():
    """Run all validation checks"""
    print("\n🔍 LLM Code Deployment API - Setup Validation\n")
    
    all_checks_passed = True
    
    # Check Python version
    print_header("Python Version")
    if not check_python_version():
        all_checks_passed = False
    
    # Check environment variables
    print_header("Environment Variables")
    env_checks = [
        check_env_var('STUDENT_SECRET', required=True),
        check_env_var('OPENAI_API_KEY', required=True),
        check_env_var('GITHUB_TOKEN', required=True),
        check_env_var('GITHUB_USERNAME', required=True),
        check_env_var('API_HOST', required=False),
        check_env_var('PORT', required=False),
    ]
    if not all(env_checks):
        all_checks_passed = False
        print("\n  💡 Copy .env.example to .env and fill in your credentials")
    
    # Check API key formats
    print_header("API Key Validation")
    if not check_api_keys():
        all_checks_passed = False
    
    # Check dependencies
    print_header("Python Dependencies")
    if not check_dependencies():
        all_checks_passed = False
        print("\n  💡 Install dependencies with: pip install -r requirements.txt")
    
    # Check directories
    print_header("Project Structure")
    if not check_directories():
        all_checks_passed = False
    
    # Test API connections
    print_header("GitHub API Connection")
    if not test_github_connection():
        all_checks_passed = False
    
    print_header("OpenAI API Connection")
    if not test_openai_connection():
        all_checks_passed = False
    
    # Final summary
    print_header("Summary")
    if all_checks_passed:
        print("\n  ✅ All checks passed! You're ready to start the server.")
        print("\n  🚀 Start the server with:")
        print("     python -m src.main")
        print("\n  🧪 Test the API with:")
        print("     python test/test_client.py")
    else:
        print("\n  ❌ Some checks failed. Please fix the issues above.")
        print("\n  📚 See SETUP.md for detailed setup instructions")
    
    print("\n" + "=" * 60 + "\n")
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
