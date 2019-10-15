from django.urls import path
from . import views

app_name = 'dataset'
urlpatterns = [
    path('search', views.search),
]