# user/urls.py

from django.urls import path
from .views import RegistrationAPIView, LoginAPIView, GetAllUser, ChangePasswordAPIView

urlpatterns = [
    path('register', RegistrationAPIView.as_view(), name='register'),
    path('login', LoginAPIView.as_view(), name='login'),
    path('getAllUser', GetAllUser.as_view(), name='getAllUser'),
    path('changePassword', ChangePasswordAPIView.as_view(), name='changePassword')
]
