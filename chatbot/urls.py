from django.urls import path
from .views import upload_text, query_chatbot, list_files, delete_file

urlpatterns = [
    path('upload/', upload_text, name='upload_text'),
    path('', query_chatbot, name='query_chatbot'),
    path('list_files/', list_files, name='list_files'),
    path('delete_file/<str:filename>/', delete_file, name='delete_file'),

]