from django.contrib.auth import logout
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from apps.user.models import CustomUser
from apps.user.serializers import (
    UserSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
    LoginSerializer,
    ForgotPasswordSerializer
)

User=CustomUser

class RegisterUser(GenericAPIView):
    """
    API view for user registration.
    Uses `UserSerializer` to validate and save the user data.
    """
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_data = serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmail(APIView):
    """
    API view to verify email using a unique link sent to the user's email.
    Decodes the `uidb64` and validates the token.
    """

    def get(self, request, uidb64, token):
        try:
            # Decode the UID and get the user
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'msg': 'Invalid verification link.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the token is valid
        if default_token_generator.check_token(user, token):
            if user.is_active:
                return Response({'msg': 'Email already verified.'}, status=status.HTTP_400_BAD_REQUEST)
            user.is_active = True
            user.save(update_fields=['is_active'])
            return Response({'msg': 'Email verified successfully.'}, status=status.HTTP_200_OK)
        return Response({'msg': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(GenericAPIView):
    """
    API view for user login.
    Scoped throttling is applied to limit the number of login attempts.
    """
    serializer_class = LoginSerializer
  
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(GenericAPIView):
    """
    API view to allow authenticated users to change their password.
    Users must be authenticated to access this view.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.change_password()
            return Response({'msg': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPassword(GenericAPIView):
    """
    API view to handle password reset requests.
    Sends a password reset email if the request is valid.
    """
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.send_reset_pass_email()
            return Response({'msg': 'Password reset email sent successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(GenericAPIView):
    """
    API view to handle the actual password reset process.
    Uses the `uid` and `token` to validate the request before resetting the password.
    """
    serializer_class = ResetPasswordSerializer

    def post(self, request, uid, token):
        serializer = self.serializer_class(data=request.data, context={'uid': uid, 'token': token})
        if serializer.is_valid():
            serializer.reset_password()
            return Response({'msg': 'Password reset successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    """
    API view to log out an authenticated user.
    Requires the user to be authenticated.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'msg': 'Logged out successfully.'})
