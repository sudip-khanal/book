from django.urls import path

from apps.user.views import (
    RegisterUser,VerifyEmail,
    UserLogin, 
    ChangePassword, 
    ForgotPassword, 
    ResetPassword,
    Logout)

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('verify_email/<str:uidb64>/<str:token>/', VerifyEmail.as_view(), name='verify_email'),
    path('login/', UserLogin.as_view(), name='login'),
    path('change_password/', ChangePassword.as_view(), name='change_password'),
    path('forgot_password/', ForgotPassword.as_view(), name='forgot_password'),
    path('reset_password/<str:uid>/<str:token>/', ResetPassword.as_view(), name='reset_password'),
    path('logout/',Logout.as_view(),name='logout')
]