from django.urls import path

from .views import RegistrationAPIView, LoginAPIView, UserRetrieveUpdateAPIView

app_name = 'authentication'
urlpatterns = [
    path('auth/login', LoginAPIView.as_view()),
    path('auth/register', RegistrationAPIView.as_view()),
    path('user', UserRetrieveUpdateAPIView.as_view()),
]