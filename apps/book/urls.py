from rest_framework.routers import DefaultRouter

from apps.book.views import BookViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'', BookViewSet, basename='book')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = router.urls
