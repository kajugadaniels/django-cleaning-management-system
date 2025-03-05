import logging
from django.core.mail import EmailMessage
from django.conf import settings

def send_otp_email(recipient_email, otp):
    """
    Sends an OTP email to the specified recipient.
    """
    subject = "Password Reset OTP"
    body = (
        "Dear User,\n\n"
        "Your OTP for password reset is: {otp}\n\n"
        "If you did not request a password reset, please ignore this email.\n\n"
        "Regards,\n"
        "Reliance Team"
    ).format(otp=otp)
    
    try:
        email_message = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient_email])
        email_message.send(fail_silently=False)
        return True
    except Exception as e:
        logging.error(f"Failed to send OTP email to {recipient_email}: {e}")
        return False
