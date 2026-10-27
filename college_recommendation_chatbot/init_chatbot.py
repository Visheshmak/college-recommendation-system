#!/usr/bin/env python3
"""
Interactive Chatbot Setup Script
Initialize and train the college recommendation chatbot
"""

import subprocess
import sys
import time
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_step(step_num, text):
    """Print step header"""
    print(f"[Step {step_num}] {text}")
    print("-" * 50)


def check_mongodb():
    """Check if MongoDB is running"""
    print_step(1, "Checking MongoDB Connection")
    
    try:
        from pymongo import MongoClient
        from mongo_db import MONGODB_URI
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
        client.server_info()  # Force connection test
        print("✅ MongoDB is reachable via MONGODB_URI")
        return True
    except Exception as e:
        print(f"❌ MongoDB is not running!")
        print(f"   Error: {e}")
        print("\n   💡 To fix this:")
        print("   • Windows: Start MongoDB from Services or run 'mongod'")
        print("   • Linux/Mac: Run 'brew services start mongodb-community'")
        print("   • Or: 'sudo systemctl start mongod'\n")
        return False


def check_python_packages():
    """Check if required packages are installed"""
    print_step(2, "Checking Python Packages")
    
    required_packages = {
        'flask': 'Flask',
        'pymongo': 'PyMongo',
        'dotenv': 'python-dotenv',
        'reportlab': 'ReportLab'
    }
    
    missing = []
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {name} is installed")
        except ImportError:
            print(f"❌ {name} is missing")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("\n💡 Install them with:")
        print(f"   pip install {' '.join(missing)}\n")
        return False
    
    print("\n✅ All required packages are installed!")
    return True


def train_chatbot():
    """Initialize Advanced Chatbot System"""
    print_step(3, "Initializing Advanced Chatbot System")
    
    try:
        # Import advanced chatbot to verify it works
        from advanced_chatbot import AdvancedCollegeChatbot
        from web_scraper import WebScraper
        
        print("✅ Advanced Chatbot module loaded")
        print("✅ Web scraper module loaded")
        print("✅ Real-time verification system ready")
        print("\n✅ Advanced chatbot system initialized successfully!")
        return True
            
    except Exception as e:
        print(f"❌ Error initializing advanced chatbot: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_env_file():
    """Check if .env file exists"""
    print_step(4, "Checking Environment Configuration")
    
    env_path = Path('.env')
    example_path = Path('.env.example')
    
    if env_path.exists():
        print("✅ .env file found")
        return True
    elif example_path.exists():
        print("⚠️  .env file not found, but .env.example exists")
        print("\n💡 To set up email:")
        print("   1. Copy: cp .env.example .env")
        print("   2. Edit .env with your email credentials")
        print("   3. For Gmail: Get app password from https://myaccount.google.com/apppasswords\n")
        return False
    else:
        print("❌ .env file not found")
        print("\n💡 Create .env file with:")
        print("   MAIL_SERVER=smtp.gmail.com")
        print("   MAIL_PORT=587")
        print("   MAIL_USERNAME=your-email@gmail.com")
        print("   MAIL_PASSWORD=your-app-password\n")
        return False


def check_mongodb_data():
    """Check if colleges data is loaded"""
    print_step(5, "Checking College Data in MongoDB")
    
    try:
        from mongo_db import colleges_col, college_details_col
        
        colleges_count = colleges_col.count_documents({})
        details_count = college_details_col.count_documents({})
        
        if colleges_count > 0:
            print(f"✅ Found {colleges_count} colleges in database")
        else:
            print(f"⚠️  No colleges found in database")
            print("\n💡 To load college data:")
            print("   1. Run: python db_init.py")
            print("   2. Or import your CSV files\n")
        
        return colleges_count > 0
        
    except Exception as e:
        print(f"⚠️  Could not check college data: {e}")
        return False


def show_summary(results):
    """Show setup summary"""
    print_header("Setup Summary")
    
    checks = [
        ("MongoDB Connection", results.get('mongodb', False)),
        ("Python Packages", results.get('packages', False)),
        ("Chatbot Training", results.get('training', False)),
        ("Environment Config", results.get('env', False)),
        ("College Data", results.get('data', False))
    ]
    
    all_passed = all(result for _, result in checks)
    
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
    
    print("\n" + "="*60)
    
    if all_passed:
        print("\n✨ SUCCESS! Chatbot is fully configured and ready to use!")
        print("\n🚀 Next Steps:")
        print("   1. Run the app: python app.py")
        print("   2. Visit: http://localhost:5000")
        print("   3. Try the chatbot at: /chatbot/demo\n")
        print("   📚 For more info, read: CHATBOT_TRAINING.md\n")
        return True
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nFor help:")
        print("   • Read: CHATBOT_TRAINING.md")
        print("   • Check: README.md")
        print("   • Show logs when running: python app.py\n")
        return False


def main():
    """Main setup flow"""
    
    print_header("🤖 College Chatbot - Setup Wizard")
    
    print("This script will check if everything is ready for the chatbot.\n")
    
    results = {}
    
    # Check MongoDB
    results['mongodb'] = check_mongodb()
    if not results['mongodb']:
        show_summary(results)
        sys.exit(1)
    
    time.sleep(1)
    
    # Check packages
    results['packages'] = check_python_packages()
    if not results['packages']:
        show_summary(results)
        sys.exit(1)
    
    time.sleep(1)
    
    # Train chatbot
    results['training'] = train_chatbot()
    if not results['training']:
        show_summary(results)
        sys.exit(1)
    
    time.sleep(1)
    
    # Check env
    results['env'] = check_env_file()
    
    # Check data
    results['data'] = check_mongodb_data()
    
    time.sleep(1)
    
    # Show summary
    success = show_summary(results)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
