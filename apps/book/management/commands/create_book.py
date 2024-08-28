import requests
from django.core.management.base import BaseCommand
from apps.book.models import Book
from apps.user.models import CustomUser

class Command(BaseCommand):
    help = "Search and fetch book details from Google Books API and insert them into the Book model by keyword"

    def add_arguments(self, parser):
        parser.add_argument('query', nargs='+', type=str)

    def handle(self, *args, **kwargs):
        query = ' '.join(kwargs['query'])
        url = f'https://www.googleapis.com/books/v1/volumes?q={query}'

        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return

        books = response.json().get('items', [])
        if not books:
            print("No books found.")
            return

        for book_data in books[:5]:  # Limiting to the first 5 results
            volume_info = book_data.get('volumeInfo', {})
            book_details = {
                'title': volume_info.get('title', 'N/A'),
                'authors': ', '.join(volume_info.get('authors', [])),
                'description': volume_info.get('description', ''),
                'published_date': volume_info.get('publishedDate', 'N/A'),
            }

            # Insert the book details into the Book model
            Book.objects.create(
                title=book_details['title'],
                author=book_details['authors'],
                # description=book_details['description'],
                created_by=CustomUser.objects.first(),
                is_active=True
                )


