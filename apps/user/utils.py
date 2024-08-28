from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

def send_verification_email(user):
    """
    Send verification email to the user
    """
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_url = f"{settings.SITE_URL}/user/verify_email/{uid}/{token}/"
    subject = 'Verify your email'
    message = f'Hi {user.username}, please verify your email by clicking the link: {verification_url}'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

def send_reset_email(user):
    """
    Send password reset email to the user
    """
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_password_url = f"{settings.SITE_URL}/user/reset_password/{uid}/{token}/"
    subject = "Password Reset"
    message = f"Hi {user.username}, please click the link to reset your password:\n{reset_password_url}"
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
