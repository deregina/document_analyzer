"""
URL configuration for the analyzer app.

This file defines the URL routes for file upload, question answering, and document management.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/upload/', views.upload_file, name='upload_file'),
    path('api/ask/', views.ask_question, name='ask_question'),
    path('api/conversation/<int:conversation_id>/', views.get_conversation, name='get_conversation'),
    path('api/documents/', views.list_documents, name='list_documents'),
    path('api/documents/<int:document_id>/delete/', views.delete_document, name='delete_document'),
]

