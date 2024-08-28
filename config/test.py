from django.test import override_settings

from rest_framework.test import APITestCase,APIClient
from rest_framework.authtoken.models import Token

from apps.user.tests.factories import UserFactory

@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True
)

class TestApi(APITestCase):

    client_class = APIClient 

    def setUp(self):
        self.client = self.client_class()  # Instantiate the client
        super().setUp() 
        super_user = UserFactory(is_superuser=True, is_staff=True,)
        user = UserFactory()
    
    @classmethod
    def create_user(cls):
        user = UserFactory()
        user.set_password('password@123')  # Set the password used for login
        user.save()
        return user
    
    def authenticate(self, user=None):
        if user is None:
            user = self.create_user()
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        return token
   
    
   


   

   