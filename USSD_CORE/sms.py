# sms.py
import africastalking
from django.conf import settings

# Initialize Africastalking once
africastalking.initialize(settings.AFRICASTALKING_USERNAME, settings.AFRICASTALKING_API_KEY)
sms_service = africastalking.SMS


def send_sms_ack(phone_number, message):
    """
    Send SMS acknowledgment to the user
    """
    try:
        response = sms_service.send(message, [phone_number])
        print(f"SMS sent to {phone_number}: {response}")
        return True
    except Exception as e:
        print(f"Failed to send SMS to {phone_number}: {e}")
        return False
