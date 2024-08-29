from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

from apps.book.models import Favorite


@receiver(post_save, sender=Favorite)
def notify_user_on_favorite(sender, instance, created, **kwargs):
    """   
    Sends an email notification to the user when they add a book to their favorites.
    """
    if created:
        user = instance.user
        book = instance.book
        subject='Book Favorited'
        message= f'You have favorited the book: {book.title}.'
        send_mail(
             subject,
             message,
             settings.EMAIL_HOST_USER,
             [user.email],
             )
