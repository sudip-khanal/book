import django_filters
from apps.user.models import CustomUser
from apps.book.models import Book,Review
User=CustomUser

class BookFilter(django_filters.FilterSet):
    """
    FilterSet for filtering books based on various fields.
    Allows filtering by title, author, creation date range, and user.
    """
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    author = django_filters.CharFilter(field_name='author', lookup_expr='iexact')
    created_at_gt = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gt')
    created_at_lt = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lt')
    user = django_filters.CharFilter(method='filter_by_user')

    class Meta:
        model = Book
        fields = ['title', 'author', 'created_at', 'created_at_lt', 'user']

    def filter_by_user(self, queryset,name,value):
        """
        Custom filter method to filter books based on the username of the creator.
        """
        return queryset.filter(created_by__username=value)



class ReviewFilter(django_filters.FilterSet):
    """
    FilterSet for filtering reviews based on related book, user, and review text.
    """
    book = django_filters.ModelChoiceFilter(queryset=Book.objects.all())
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    review_text = django_filters.CharFilter(field_name='review_text',lookup_expr='iexact')
    class Meta:
        model = Review
        fields = ['book', 'user', 'review_text']