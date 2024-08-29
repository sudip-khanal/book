import time

from rest_framework.throttling import BaseThrottle
from rest_framework.exceptions import Throttled


class BookThrottle(BaseThrottle):
    """
    Custom throttle class for the BookViewSet.
    Allows up to:
    - 5 requests per hour for unauthenticated users (based on IP).
    - 20 requests per hour for authenticated users (based on user ID).
    - Unlimited requests for superusers.
    """
    request_history = {}

    def allow_request(self, request, view):
        if request.user and request.user.is_authenticated and request.user.is_superuser:
            return True
        # Identify the user or IP address making the request
        user_ident = self.get_ident(request)
        current_time = time.time()

        # Initialize or update the user's request history
        if user_ident not in self.request_history:
            self.request_history[user_ident] = []

        # Filter out requests that are older than 1 hour (3600 seconds)
        self.request_history[user_ident] = [
            timestamp for timestamp in self.request_history[user_ident]
            if current_time - timestamp < 3600
        ]

        if request.user and request.user.is_authenticated:
            request_limit = 5 
            throttled_message = "Request limit exceeded: You can make up to 5 requests per hour."
        else:
            request_limit = 3
            throttled_message = "Request limit exceeded: You can make up to 3 requests per hour."

        if len(self.request_history[user_ident]) < request_limit:
            self.request_history[user_ident].append(current_time)
            return True

        # Throttle the request if the user has reached their limit
        raise Throttled(detail=throttled_message)
    
    def wait(self):
        """
        Return the time remaining until the next request is allowed if throttled.
        """
        user_ident = self.get_ident(self.request)
        last_request_time = self.request_history[user_ident][0] if user_ident in self.request_history else 0
        return max(0, 3600 - (time.time() - last_request_time))

    def get_ident(self, request):
        if request.user and request.user.is_authenticated:
            return request.user.id  
        else:
            xff = request.META.get('HTTP_X_FORWARDED_FOR')
            remote_addr = request.META.get('REMOTE_ADDR')
            return xff.split(',')[0].strip() if xff else remote_addr
