from rest_framework.pagination import PageNumberPagination

class BookPagination(PageNumberPagination):
    page_size=5
    page_size_query_param='records'
    max_page_size=10
