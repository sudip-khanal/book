from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate

from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers

from apps.user.tasks import send_verification_email_task
from apps.user.utils import send_reset_email
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'confirm_password'
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])       
        user.is_active = False  # Inactive until email is verified
        user.save()
        print(f"Scheduling send_verification_email_task for user {user.id}")
        transaction.on_commit(lambda:send_verification_email_task.delay(user.id)) 
        return user
       

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    def validate(self, attrs):
         # Authenticate the user with the username and password
        username = attrs.get('username', '')
        password = attrs.get('password', '')
        user = authenticate(username=username, password=password)

        # if authentication fails or user is inactive
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, verify your email first')
         # Return user data with token
        return {
            'username': user.username,
            'email':user.email,
            'token': Token.objects.get_or_create(user=user)[0].key
        }
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):       
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({"old_password": "Wrong password."})
        elif attrs['new_password'] != attrs['confirm_new_password']: # Check if the new passwords match
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs
    
    def change_password(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password']) # Save the new password
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)  
        except User.DoesNotExist:
            raise serializers.ValidationError(" User not found with this email address.")
        return value
    
    def send_reset_pass_email(self):
        send_reset_email(self.user)

    def send_reset_pass_email(self):
        send_reset_email(self.user)

    
# Serializer for resetting the user's password
class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']: # Check if the new passwords match
            raise serializers.ValidationError({"password": "Passwords do not match."})
        try:
            uid = force_bytes(urlsafe_base64_decode(self.context['uid']))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"msg": "Invalid link."})
        
        if not default_token_generator.check_token(self.user, self.context['token']):
            raise serializers.ValidationError({"msg": "Invalid token."})
        return attrs
    # Save the new password
    def reset_password(self):
        user=self.user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user