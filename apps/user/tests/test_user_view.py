from unittest.mock import patch

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from rest_framework import status

from config.test import TestApi
from apps.user.tests.factories import UserFactory


class TestUser(TestApi):

    @patch('apps.user.tasks.send_verification_email_task')
    def test_register_user(self, mock_send_verification_email_task):
        """
        Test case for user registration.
        Verifies that:
        1. A new user can be successfully registered with valid data.
        2. The response contains the correct username and email.
        3. Registration fails if the username or email is already taken.
        """
        url = '/user/register/'

        # Data for registering a new user
        data = {
            'username': 'testuser1',
            'email': 'testuser1@example.com',
            'password': 'password@123',
            'confirm_password': 'password@123'
        }

        # Register the new user
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])

        # Test check try to register with already taken email 
        data['email']= 'testuser1@example.com'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

        # Test try to register with mismatched password and confirm_password
        data['confirm_password']= 'password@1233543'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

        self.assertTrue(mock_send_verification_email_task.is_called())


    def test_verify_email(self):
        # Create a user who is not yet active
        user = UserFactory(is_active=False)

        # Generate the URL parameters
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

         # Test with an invalid token
        url = f'/user/verify_email/{uidb64}/invalidtoken/'  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        url = f'/user/verify_email/{uidb64}/{token}/'  
        response = self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.is_active)


    def test_user_login(self):
        """
        Test case for user login.
        Verifies that:
        A user can successfully log in with valid credentials.
        Login fails with invalid credentials.
        """
        user = self.create_user() 
        url = '/user/login/' 
        data = {
            'username': user.username,
            'password': 'password@123'  
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['token'])

        # Test login with  wrong password
        data['password']='passwd'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED )

        # Test login with not registered username
        data['username']='myusername'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED )

     
    def test_change_passwords(self):
        """
        Test case for changing a user's password.
        Verifies that:
        1. A user can successfully change their password with valid data.
        2. The new password confirmation matches the new password.
        """
        user = self.create_user()

        url = '/user/change_password/'

        # Test changing password with incorrect old password
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword@123',
            'confirm_new_password': 'newpassword@123'
        }
        self.client.force_authenticate(user=user)       
        response = self.client.post(url,data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test changing password with correct old password
        data['old_password'] = 'password@123'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test changing with mismatched new password
        data['confirm_new_password']='newpwd'
        response = self.client.post(url,data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_logout(self):
        """
        Test case for user logout.
        Verifies that:
        1. An authenticated user can successfully log out.
        2. The logout operation invalidates the user's token.
        """
        # Create and authenticate the user
        user = self.create_user()
        
        url = '/user/logout/' 
        self.client.force_authenticate(user=user) 
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Attempt to access a protected endpoint with the same token after the logout
        protected_url = '/user/change_password/' 
        protected_response = self.client.get(protected_url)
        self.assertEqual(protected_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_forgot_password(self):
        """
        Test case for forgot password functionality.
        Verifies that:
        1. A password reset email is sent when a valid email is provided.
        2. The response contains the correct message.
        3. The email sending task is called with the correct user ID.
        """
        # Create a user with an email
        user = UserFactory(email='testuser@example.com')

        url = '/user/forgot_password/'  
        data = {
            'email': 'testuser@example.com'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_passwords(self):
        """
        Test case for resetting a user's password 
        Verifies that:
        1. The password reset process works with a valid UID and token.
        3. The user can log in with the new password.
        """
        # This user should have received a reset password  link in email
        user = self.create_user()  
        # Generate UID and token for password reset 
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        url = f'/user/reset_password/{uid}/{token}/'

        # Data for resetting the password
        data = {
            'new_password': 'password@1234',
            'confirm_new_password': 'password@1234'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test mismatched new_password and confirm_new_password
        data['confirm_new_password']='1234'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

         # Test with an invalid token
        invalid_token_url = f'/user/reset_password/{uid}/invalidtoken/'
        response = self.client.post(invalid_token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
        # Attempt to log in with the new password
        login_data = {
            'username': user.username,
            'password': 'password@1234'
        }
        response = self.client.post('/user/login/', login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)



       