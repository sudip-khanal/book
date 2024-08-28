from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token

class CustomUser(AbstractUser):
    email=models.EmailField(unique=True,blank=False,null=False)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.username
    
# Signal receiver to automatically create an authentication token for a new user.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Creates an authentication token for a newly created user instance.
    """
    if created:
        Token.objects.create(user=instance)