import os
import base64
import requests
from datetime import datetime
import django

# --- Setup Django environment ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KAG_USSD.settings")
django.setup()

from django.conf import settings

from django.test import TestCase
from django.conf import settings

class MpesaSettingsTest(TestCase):
    def test_consumer_key_loaded(self):
        self.assertEqual(settings.MPESA_CONSUMER_KEY, "your_consumer_key")


# --- Load M-Pesa settings from Django ---
CONSUMER_KEY = settings.MPESA_CONSUMER_KEY
CONSUMER_SECRET = settings.MPESA_CONSUMER_SECRET
SHORTCODE = settings.MPESA_SHORTCODE
PASSKEY = settings.MPESA_PASSKEY
CALLBACK_URL = settings.MPESA_CALLBACK_URL


def get_access_token():
    """Get OAuth token from Safaricom API"""
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(api_url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    json_response = response.json()
    return json_response.get("access_token")


def stk_push(phone_number: str, amount: int, account_reference="Test123", transaction_desc="Test Payment"):
    """Initiate M-Pesa STK Push"""
    access_token = get_access_token()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Password is base64(SHORTCODE + PASSKEY + TIMESTAMP)
    password = base64.b64encode((SHORTCODE + PASSKEY + timestamp).encode()).decode("utf-8")

    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {access_token}"}

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,  # Customer phone number
        "PartyB": SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()


if __name__ == "__main__":
    # Test with your Safaricom test phone number from Daraja sandbox
    test_phone = "254714441708"   # Replace with sandbox test number
    test_amount = 10

    print("🚀 Initiating STK Push...")
    result = stk_push(test_phone, test_amount)
    print("✅ Response:", result)



# import os
# import django
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KAG_USSD.settings")  # replace with actual project name
# django.setup()
#
# from django.conf import settings
#
# print(settings.MPESA_CONSUMER_KEY)
