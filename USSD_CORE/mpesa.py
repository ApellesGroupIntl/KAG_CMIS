# mpesa.py - Production Ready
import requests
from django.conf import settings
from datetime import datetime
import base64
import json
import logging
from decouple import config
from requests.auth import HTTPBasicAuth


# Set up logging
logger = logging.getLogger(__name__)


def get_access_token():
    """Get M-Pesa access token for production"""
    consumer_key = config("MPESA_CONSUMER_KEY")
    consumer_secret = config("MPESA_CONSUMER_SECRET")

    # Validate credentials
    if not consumer_key or not consumer_secret:
        logger.error("M-Pesa credentials not configured")
        raise Exception("M-Pesa credentials not configured")

    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth_string = f"{consumer_key}:{consumer_secret}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_auth}",
        # "Content-Type": "application/json"
    }

    try:
        logger.info("Requesting M-Pesa access token")
        response = requests.get(auth_url, headers=headers, timeout=30)
        print("DEBUG Auth response:", response.status_code, response.text)

        if response.status_code != 200:
            logger.error(f"M-Pesa auth failed: {response.status_code} - {response.text}")
            raise Exception(f"M-Pesa authentication failed: {response.status_code}")

        data = response.json()
        access_token = data.get("access_token")

        if not access_token:
            logger.error("No access token in response")
            raise Exception("No access token received from M-Pesa")

        logger.info("Access token obtained successfully")
        return access_token

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error getting access token: {e}")
        raise Exception(f"Network error: {e}")

    except Exception as e:
        logger.error(f"Error getting access token: {e}")
        raise


def generate_password():
    """Generate M-Pesa API password"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    shortcode = settings.MPESA_SHORTCODE
    passkey = settings.MPESA_PASSKEY

    data_to_encode = f"{shortcode}{passkey}{timestamp}"
    password = base64.b64encode(data_to_encode.encode()).decode("utf-8")
    return password, timestamp


def format_phone_number(phone_number):
    """Format phone number to 254 format"""
    if phone_number.startswith("+"):
        phone_number = phone_number[1:]
    if phone_number.startswith("0"):
        phone_number = "254" + phone_number[1:]

    # Validate phone number format
    if len(phone_number) != 12 or not phone_number.startswith("254"):
        raise ValueError(f"Invalid phone number format: {phone_number}")

    return phone_number


def stk_push_request(phone_number, amount, account_reference, transaction_desc="USSD Payment"):
    """
    Production STK Push request
    """
    try:
        logger.info(f"Initiating STK Push: {phone_number}, Amount: {amount}")

        # Get access token
        access_token = get_access_token()

        # Generate password
        password, timestamp = generate_password()

        # Format phone number
        formatted_phone = format_phone_number(phone_number)

        # Prepare payload
        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(float(amount)),
            "PartyA": formatted_phone,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": formatted_phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": account_reference[:12],
            "TransactionDesc": transaction_desc[:20],
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Send STK Push request
        logger.info("Sending STK Push request to M-Pesa")
        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            print("DEBUG STK Response:", response.text)  # 👈 Add this
            logger.error(f"STK Push failed: {response.status_code} - {response.text}")
            raise Exception(f"STK Push failed: {response.status_code}")

        result = response.json()

        if result.get("ResponseCode") == "0":
            logger.info("STK Push initiated successfully")
            return result
        else:
            error_msg = result.get("ResponseDescription", "Unknown error")
            logger.error(f"STK Push error: {error_msg}")
            raise Exception(f"M-Pesa Error: {error_msg}")

    except ValueError as e:
        logger.error(f"Phone number validation error: {e}")
        raise Exception(f"Invalid phone number: {e}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error in STK Push: {e}")
        raise Exception(f"Network error: Please try again")

    except Exception as e:
        logger.error(f"STK Push error: {e}")
        raise


# # mpesa.py
# import requests
# from django.conf import settings
# from datetime import datetime
# import base64
# import json
#
#
# def get_access_token():
#     """Get M-Pesa access token with detailed error reporting"""
#     consumer_key = settings.MPESA_CONSUMER_KEY
#     consumer_secret = settings.MPESA_CONSUMER_SECRET
#
#     # Debug: Check if credentials are set
#     if not consumer_key or not consumer_secret:
#         print("ERROR: M-Pesa credentials are not set in settings.py")
#         return None
#
#     print(f"DEBUG: Using Consumer Key: {consumer_key}")
#     print(f"DEBUG: Using Consumer Secret: {consumer_secret[:10]}...")  # First 10 chars only
#
#     auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
#
#     # Encode credentials
#     auth_string = f"{consumer_key}:{consumer_secret}"
#     encoded_auth = base64.b64encode(auth_string.encode()).decode()
#
#     headers = {
#         "Authorization": f"Basic {encoded_auth}",
#         "Content-Type": "application/json"
#     }
#
#     try:
#         print("DEBUG: Requesting access token from Safaricom...")
#         response = requests.get(auth_url, headers=headers, timeout=30)
#
#         print(f"DEBUG: Response Status: {response.status_code}")
#         print(f"DEBUG: Response Text: {response.text}")
#
#         if response.status_code == 400:
#             print("ERROR: 400 Bad Request - Likely invalid credentials")
#             print("Please check your MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET")
#             return None
#
#         response.raise_for_status()
#
#         data = response.json()
#         access_token = data.get("access_token")
#
#         if access_token:
#             print("DEBUG: Successfully obtained access token")
#             return access_token
#         else:
#             print("ERROR: No access token in response")
#             return None
#
#     except requests.exceptions.RequestException as e:
#         print(f"ERROR: Network error - {e}")
#         return None
#     except Exception as e:
#         print(f"ERROR: Unexpected error - {e}")
#         return None
#
#
# def generate_password():
#     """Generate M-Pesa API password"""
#     timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
#     shortcode = settings.MPESA_SHORTCODE
#     passkey = settings.MPESA_PASSKEY
#
#     print(f"DEBUG: Using Shortcode: {shortcode}")
#     print(f"DEBUG: Using Passkey: {passkey[:10]}...")
#
#     data_to_encode = f"{shortcode}{passkey}{timestamp}"
#     password = base64.b64encode(data_to_encode.encode()).decode("utf-8")
#     return password, timestamp
#
#
# def stk_push_request(phone_number, amount, account_reference, transaction_desc="USSD Payment"):
#     """
#     Trigger STK Push to customer's phone
#     """
#     print(f"DEBUG: Starting STK Push for {phone_number}, Amount: {amount}")
#
#     access_token = get_access_token()
#     if not access_token:
#         print("ERROR: Cannot proceed without access token")
#         return {"error": "Failed to get access token"}
#
#     password, timestamp = generate_password()
#
#     # Format phone number
#     if phone_number.startswith("+"):
#         phone_number = phone_number[1:]
#     if phone_number.startswith("0"):
#         phone_number = "254" + phone_number[1:]
#
#     # Use sandbox test number if in development
#     if settings.DEBUG:
#         phone_number = "254708374149"  # Sandbox test number
#         print(f"DEBUG: Using sandbox test number: {phone_number}")
#
#     payload = {
#         "BusinessShortCode": settings.MPESA_SHORTCODE,
#         "Password": password,
#         "Timestamp": timestamp,
#         "TransactionType": "CustomerPayBillOnline",
#         "Amount": int(float(amount)),
#         "PartyA": phone_number,
#         "PartyB": settings.MPESA_SHORTCODE,
#         "PhoneNumber": phone_number,
#         "CallBackURL": settings.MPESA_CALLBACK_URL,
#         "AccountReference": account_reference[:12],
#         "TransactionDesc": transaction_desc[:20],
#     }
#
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }
#
#     try:
#         print("DEBUG: Sending STK Push request...")
#         response = requests.post(
#             "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
#             json=payload,
#             headers=headers,
#             timeout=30
#         )
#
#         print(f"DEBUG: STK Response Status: {response.status_code}")
#         print(f"DEBUG: STK Response Text: {response.text}")
#
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return {"error": f"STK Push failed with status {response.status_code}"}
#
#     except Exception as e:
#         error_msg = f"STK Push request failed: {str(e)}"
#         print(f"ERROR: {error_msg}")
#         return {"error": error_msg}