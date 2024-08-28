import logging
from celery import shared_task

from django.contrib.auth import get_user_model
from django.core.management import call_command 

from apps.user.utils import send_verification_email

User = get_user_model()
logger = logging.getLogger(__name__)

@shared_task(name='send_verification_email')
def send_verification_email_task(user_id):
    """
    Task to send verification email
    """
    user = User.objects.filter(id=user_id).first()  
    if user:
        send_verification_email(user)
    else:
        logger.error("User not found")


@shared_task
def create_user_task():
    """
    Task to create random user from the custom django command create_user 
    """
    call_command("create_user", 2)
