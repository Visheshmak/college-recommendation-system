"""
Email Configuration Diagnostic Tool
Run this to test your email settings
"""

import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "").strip()
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "").strip()

print("=" * 60)
print("📧 EMAIL CONFIGURATION DIAGNOSTIC TEST")
print("=" * 60)

print(f"\n📋 Configuration Details:")
print(f"   SMTP Server: {MAIL_SERVER}")
print(f"   SMTP Port: {MAIL_PORT}")
print(f"   Username: {MAIL_USERNAME if MAIL_USERNAME else '❌ NOT SET'}")
print(f"   Password: {'✓ Set' if MAIL_PASSWORD else '❌ NOT SET'}")
print(f"   Password Length: {len(MAIL_PASSWORD)} characters")

if not MAIL_USERNAME or not MAIL_PASSWORD:
    print("\n❌ ERROR: Email credentials are missing in .env file!")
    print("Please set MAIL_USERNAME and MAIL_PASSWORD in .env")
    exit(1)

print(f"\n🔍 Testing SMTP Connection...")
try:
    server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=10)
    print(f"   ✅ Connected to {MAIL_SERVER}:{MAIL_PORT}")
    
    print(f"\n🔍 Testing STARTTLS...")
    server.starttls()
    print(f"   ✅ STARTTLS successful")
    
    print(f"\n🔍 Testing Login with provided credentials...")
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    print(f"   ✅ LOGIN SUCCESSFUL!")
    
    server.quit()
    print(f"\n✅ ALL TESTS PASSED - Email is ready to use!\n")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"   ❌ AUTHENTICATION FAILED")
    print(f"   Error: {e}")
    print(f"\n🔧 SOLUTIONS:")
    print(f"   1. For Gmail: Use App Password (not regular password)")
    print(f"      Visit: https://myaccount.google.com/apppasswords")
    print(f"   2. Ensure 2-Step Verification is enabled on Gmail")
    print(f"   3. Check that password in .env has no extra quotes or spaces")
    
except smtplib.SMTPException as e:
    print(f"   ❌ SMTP ERROR: {e}")
    print(f"\n🔧 SOLUTIONS:")
    print(f"   1. Check your internet connection")
    print(f"   2. Verify firewall is not blocking SMTP port {MAIL_PORT}")
    print(f"   3. Try a different SMTP server")
    
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    print(f"\n🔧 SOLUTIONS:")
    print(f"   1. Check internet connectivity")
    print(f"   2. Verify SMTP server address and port")
    print(f"   3. Check firewall settings")
