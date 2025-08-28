import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
from base64 import b64encode
from datetime import datetime

def generate_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
    return response.json().get('access_token')

def generate_password():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    password = b64encode(data.encode()).decode()
    return password, timestamp
