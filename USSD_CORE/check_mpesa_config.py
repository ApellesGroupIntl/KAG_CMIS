# emergency_debug.py
import os
import django
import requests
import base64
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KAG_USSD.settings')
django.setup()

print("🚨 EMERGENCY CREDENTIALS DEBUG 🚨")
print("=" * 50)

# Check what's actually in your settings
consumer_key = settings.MPESA_CONSUMER_KEY
consumer_secret = settings.MPESA_CONSUMER_SECRET

print(f"Consumer Key: '{consumer_key}'")
print(f"Consumer Secret: '{consumer_secret}'")
print(f"Key Length: {len(consumer_key)}")
print(f"Secret Length: {len(consumer_secret)}")

# Check if they contain placeholders
if any(x in consumer_key.lower() for x in ['your_', 'example', 'placeholder']):
    print("❌ CONSUMER KEY CONTAINS PLACEHOLDER TEXT!")

if any(x in consumer_secret.lower() for x in ['your_', 'example', 'placeholder']):
    print("❌ CONSUMER SECRET CONTAINS PLACEHOLDER TEXT!")

# Test the credentials directly
print("\n🔐 Testing credentials with Safaricom...")
auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
auth_string = f"{consumer_key}:{consumer_secret}"
encoded_auth = base64.b64encode(auth_string.encode()).decode()

headers = {
    "Authorization": f"Basic {encoded_auth}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(auth_url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 400:
        print("❌ 400 ERROR: Invalid credentials")
        print("💡 IMMEDIATE ACTION REQUIRED:")
        print("1. Login to Safaricom Developer Portal")
        print("2. Go to 'My Applications'")
        print("3. Copy the EXACT Consumer Key and Secret")
        print("4. Update settings.py with REAL values")

except Exception as e:
    print(f"❌ Connection Error: {e}")

print("\n🆘 If credentials are correct but still getting 400:")
print("1. Contact Safaricom Support: +254 711 086 000")
print("2. Ensure your account is activated")
print("3. Check if you're using sandbox, not production")