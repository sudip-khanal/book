import factory
from apps.book.models import Book, Favorite
from apps.user.tests.factories import UserFactory


class BookFactory(factory.django.DjangoModelFactory):
    created_by = factory.SubFactory(UserFactory)
    
    class Meta:
        model = Book

class FavoriteFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    book = factory.SubFactory(BookFactory)

    class Meta:
        model = Favorite
