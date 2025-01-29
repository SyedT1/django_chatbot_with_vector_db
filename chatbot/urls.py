from django.urls import path
from .views import upload_text, query_chatbot

urlpatterns = [
    path('upload/', upload_text, name='upload_text'),
    path('', query_chatbot, name='query_chatbot'),
]
