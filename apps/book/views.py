from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from apps.book.throttling import BookThrottle
from apps.book.pagination import BookPagination
from apps.book.models import Book, Favorite, Review
from apps.book.cache import top_book_cache
from apps.book.filters import BookFilter, ReviewFilter
from apps.book.serializers import (
    BookSerializer,
    FavoriteSerializer,
    FavoriteBookSerializer,
    ReviewSerializer
)


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing books.
    Provides actions for retrieving, updating, deleting books,
    and handling favorites and top-rated books.
    """
    queryset = Book.objects.filter(is_active=True)
    serializer_class = BookSerializer
    throttle_classes = [BookThrottle]  
    pagination_class= BookPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookFilter

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific book with its reviews and average rating.
        Applies custom throttle for this action.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Retrieve all reviews for the book
        reviews = Review.objects.filter(book=instance)
        review_serializer = ReviewSerializer(reviews, many=True)
        
        # Calculate the average rating for the book
        average_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        
        # Prepare the response data
        response_data = serializer.data
        response_data['average_rating'] = average_rating
        response_data['reviews'] = review_serializer.data
        
        return Response(response_data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft-delete a book by marking it as inactive.
        Only the creator of the book has permission to delete it.
        """
        instance = self.get_object()
        if instance.created_by != request.user:
            return Response(
                {"msg": "You don't have permission to delete this book."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_destroy(instance)
        return Response({"msg": "Book deleted."}, status=status.HTTP_200_OK)
    
    def perform_destroy(self, instance):
        """
        Mark the book as inactive instead of permanently deleting it.
        """
        instance.is_active = False
        instance.save(update_fields=['is_active'])

    @action(
        detail=True, 
        methods=['post'], 
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """
        Add a book to the user's favorites.
        """
        book = self.get_object()
        data = {'book': book.id, 'user': request.user.id}
        serializer = FavoriteSerializer(data=data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(
        detail=True, 
        methods=['delete'], 
        permission_classes=[IsAuthenticated]
    )
    def unfavorite(self, request, pk=None):
        """
        Remove a book from the user's favorites.
        """
        book = self.get_object()
        user = request.user
        favorite = Favorite.objects.filter(book=book, user=user)
        
        if favorite.exists():
            favorite.delete()
            return Response(
                {'msg': 'Book removed from favorites successfully.'}, 
                status=status.HTTP_200_OK
            )
        return Response(
            {'msg': 'You have not favorited this book.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(
        detail=False, 
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def my_favorites(self, request):
        """
        Get the list of books the user has favorited.
        """
        favorites = Favorite.objects.filter(user=request.user)
        serializer = FavoriteBookSerializer(favorites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_top_rated_books(self):
        """
        Get the books with the highest average rating, limited to the top 10.
        """
        return Review.objects.values('book').annotate(avg_rating=Avg('rating')).order_by('-avg_rating')[:10]
    
    @action(
        detail=False,
        methods=['get'],
        url_path='top-10-rated'
    )
    def top_rated(self, request):
        """
        Get the top 10 highest-rated books based on average ratings.
        The results are cached for efficiency.
        """
        cache_key = 'top_10_rated_books'
        top_rated_books = top_book_cache(cache_key, self.get_top_rated_books)

        if top_rated_books:
            top_rated_books_list = []
            for book_info in top_rated_books:
                book_id = book_info['book']
                average_rating = book_info['avg_rating']
                book = Book.objects.get(id=book_id)

                serializer = self.get_serializer(book)
                reviews = Review.objects.filter(book=book)
                review_serializer = ReviewSerializer(reviews, many=True)

                book_data = serializer.data
                book_data['average_rating'] = average_rating
                book_data['reviews'] = review_serializer.data

                top_rated_books_list.append(book_data)
            return Response(top_rated_books_list)
        
        return Response({"detail": "No reviews found."}, status=status.HTTP_404_NOT_FOUND)


class ReviewViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    ViewSet for managing reviews.
    Provides actions for creating and listing reviews.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReviewFilter
