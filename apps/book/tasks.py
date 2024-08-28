import logging

from celery import shared_task

from django.core.management import call_command 

logger = logging.getLogger(__name__)


@shared_task
def create_book_task(query):
    """
    Task to call django custom command create_book 
    """
    call_command('create_book', query)