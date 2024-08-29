from django.db.models.signals import post_save
from django.dispatch import receiver

from django.apps import AppConfig

class BookConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.book'


    def ready(self):
        from apps.book import signals  


