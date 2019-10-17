from django.urls import path
from .views import *

app_name = 'dataset'
urlpatterns = [
    # path('dataset/<int:pk>',  DatasetRetrieveAPIView.as_view()),
    # path('dataset',  DatasetCreateAPIView.as_view()),
    path('dataset/photo', PhotoAddAPIView.as_view()),
    path('dataset/photo/<int:pk>', PhotoRemoveAPIView.as_view()),
]