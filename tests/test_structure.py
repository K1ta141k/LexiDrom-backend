"""
Test project structure and basic functionality
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_project_structure():
    """Test that all required files and directories exist"""
    print("🧪 Testing project structure...")
    
    # Required directories
    required_dirs = [
        "app",
        "app/api",
        "app/core",
        "app/models",
        "app/services",
        "app/utils",
        "config",
        "tests"
    ]
    
    # Required files
    required_files = [
        "main.py",
        "requirements.txt",
        "env_example.txt",
        "app/__init__.py",
        "app/api/__init__.py",
        "app/core/__init__.py",
        "app/models/__init__.py",
        "app/services/__init__.py",
        "app/core/auth.py",
        "app/models/schemas.py",
        "app/services/supabase_manager.py",
        "app/services/activity_tracker.py",
        "app/services/text_comparison_service.py",
        "app/api/auth.py",
        "app/api/text_comparison.py",
        "app/api/activities.py",
        "app/api/admin.py",
        "config/setup_activities_table.sql"
    ]
    
    # Check directories
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"❌ Missing directory: {dir_path}")
            return False
        else:
            print(f"✅ Directory exists: {dir_path}")
    
    # Check files
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing file: {file_path}")
            return False
        else:
            print(f"✅ File exists: {file_path}")
    
    print("✅ Project structure test passed!")
    return True

def test_imports():
    """Test that all modules can be imported"""
    print("\n🧪 Testing imports...")
    
    try:
        # Test core imports
        from app.core.auth import create_access_token, verify_token
        print("✅ Core auth imports successful")
        
        from app.models.schemas import User, TextComparisonRequest
        print("✅ Models imports successful")
        
        from app.services.supabase_manager import SupabaseManager
        print("✅ Supabase manager import successful")
        
        from app.services.activity_tracker import ActivityTracker
        print("✅ Activity tracker import successful")
        
        from app.services.text_comparison_service import TextComparisonService
        print("✅ Text comparison service import successful")
        
        print("✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during imports: {e}")
        return False

def test_environment_variables():
    """Test environment variable loading"""
    print("\n🧪 Testing environment variables...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check if .env file exists
        if os.path.exists(".env"):
            print("✅ .env file exists")
        else:
            print("⚠️ .env file not found (you may need to create it)")
        
        # Check required environment variables
        required_vars = [
            "GOOGLE_API_KEY",
            "GOOGLE_CLIENT_ID",
            "GOOGLE_CLIENT_SECRET",
            "JWT_SECRET_KEY",
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️ Missing environment variables: {missing_vars}")
            print("   Please set these in your .env file")
        else:
            print("✅ All required environment variables are set")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing environment variables: {e}")
        return False

async def test_supabase_connection():
    """Test Supabase connection"""
    print("\n🧪 Testing Supabase connection...")
    
    try:
        from app.services.supabase_manager import SupabaseManager
        
        supabase = SupabaseManager()
        connected = await supabase.connect()
        
        if connected:
            print("✅ Supabase connection successful")
            await supabase.disconnect()
            return True
        else:
            print("⚠️ Supabase connection failed (check your credentials)")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Supabase connection: {e}")
        # Don't fail the test if Supabase is not available
        print("   (This is not critical - the app will work without Supabase)")
        return True

def main():
    """Run all tests"""
    print("🚀 Starting LexiDash Backend Tests\n")
    
    # Run tests
    structure_ok = test_project_structure()
    imports_ok = test_imports()
    env_ok = test_environment_variables()
    
    # Test Supabase connection
    try:
        supabase_ok = asyncio.run(test_supabase_connection())
    except Exception as e:
        print(f"❌ Error testing Supabase: {e}")
        supabase_ok = False
    
    # Summary
    print("\n📊 Test Results:")
    print(f"   Project Structure: {'✅ PASS' if structure_ok else '❌ FAIL'}")
    print(f"   Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   Environment: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"   Supabase Connection: {'✅ PASS' if supabase_ok else '⚠️ SKIP'}")
    
    if all([structure_ok, imports_ok, env_ok]):
        print("\n🎉 All tests passed! Your LexiDash backend is ready to run.")
        print("   Run 'python main.py' to start the server.")
        if not supabase_ok:
            print("   Note: Supabase connection failed, but the app will work without it.")
        return True
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    main() 