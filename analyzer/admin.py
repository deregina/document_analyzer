"""
Admin configuration for the analyzer app.

This module registers models in the Django admin interface.
"""
from django.contrib import admin
from .models import Document, Conversation, QuestionAnswer, Chunk


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for Document model."""
    list_display = ['filename', 'file_type', 'uploaded_at', 'file_size']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['filename', 'parsed_content']
    readonly_fields = ['uploaded_at', 'file_size']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin interface for Conversation model."""
    list_display = ['id', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']


@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    """Admin interface for Chunk model."""
    list_display = ['id', 'document', 'chunk_index', 'content_preview']
    list_filter = ['document']
    search_fields = ['content', 'document__filename']
    readonly_fields = ['start_char', 'end_char']
    
    def content_preview(self, obj):
        """Show a preview of the chunk content."""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    """Admin interface for QuestionAnswer model."""
    list_display = ['id', 'conversation', 'question', 'created_at']
    list_filter = ['created_at', 'conversation']
    search_fields = ['question', 'answer']
    filter_horizontal = ['source_documents', 'source_chunks']

