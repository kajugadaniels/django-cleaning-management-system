import random
import logging
from datetime import timedelta
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

def generate_otp(length=7):
    """
    Generate a numeric OTP of a given length.
    """
    return ''.join(str(random.randint(0, 9)) for _ in range(length))

def send_email(subject, message, recipient_list):
    """
    Send an email using Django's email backend.
    Returns True if the email is sent successfully, otherwise False.
    """
    from django.core.mail import send_mail
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False

def send_sms(phone_number, message):
    """
    Send an SMS to the provided phone number.
    This function should integrate with an SMS gateway.
    Here we simulate SMS sending.
    """
    logger.info(f"Simulated SMS sending to {phone_number}: {message}")
    # Integrate with your SMS provider here.
    return True
