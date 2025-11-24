"""
Models for the document analyzer application.

This module defines the database models for storing uploaded files,
their parsed content, and conversation history.
"""
from django.db import models
from django.utils import timezone
import os


class Document(models.Model):
    """
    Model to store uploaded documents.
    
    Attributes:
        file: The uploaded file
        filename: Original filename
        file_type: Type of file (pdf, docx, xlsx, email)
        uploaded_at: Timestamp when file was uploaded
        parsed_content: Extracted text content from the file
        file_size: Size of the file in bytes
    """
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('xlsx', 'Excel Spreadsheet'),
        ('email', 'Email'),
        ('other', 'Other'),
    ]
    
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    parsed_content = models.TextField(blank=True, help_text="Extracted text content from the document")
    file_size = models.BigIntegerField(help_text="File size in bytes")
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
    
    def __str__(self):
        """String representation of the document."""
        return self.filename
    
    def delete(self, *args, **kwargs):
        """Override delete to also remove the file from filesystem."""
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)


class Chunk(models.Model):
    """
    Model to store document chunks (text segments).
    
    Documents are split into chunks to enable better retrieval
    and allow the LLM to reference specific parts of documents.
    
    Attributes:
        document: Foreign key to the parent document
        chunk_index: Index of this chunk within the document (0-based)
        content: The text content of this chunk
        start_char: Starting character position in original document
        end_char: Ending character position in original document
    """
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.IntegerField(help_text="Index of this chunk within the document")
    content = models.TextField(help_text="Text content of this chunk")
    start_char = models.IntegerField(default=0, help_text="Starting character position")
    end_char = models.IntegerField(default=0, help_text="Ending character position")
    
    class Meta:
        ordering = ['document', 'chunk_index']
        unique_together = ['document', 'chunk_index']
        verbose_name = 'Document Chunk'
        verbose_name_plural = 'Document Chunks'
    
    def __str__(self):
        """String representation of the chunk."""
        return f"{self.document.filename} - Chunk {self.chunk_index}"


class Conversation(models.Model):
    """
    Model to store conversation sessions.
    
    Each conversation can have multiple questions and answers.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
    
    def __str__(self):
        """String representation of the conversation."""
        return f"Conversation {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class QuestionAnswer(models.Model):
    """
    Model to store questions and answers in a conversation.
    
    Attributes:
        conversation: Foreign key to the conversation
        question: User's question
        answer: AI-generated answer
        source_documents: Many-to-many relationship with documents used for answering
        source_chunks: Many-to-many relationship with chunks used for answering
        created_at: Timestamp when Q&A was created
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='qa_pairs')
    question = models.TextField()
    answer = models.TextField()
    source_documents = models.ManyToManyField(Document, related_name='qa_pairs', blank=True)
    source_chunks = models.ManyToManyField(Chunk, related_name='qa_pairs', blank=True, help_text="Specific chunks used to generate the answer")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Question & Answer'
        verbose_name_plural = 'Questions & Answers'
    
    def __str__(self):
        """String representation of the Q&A pair."""
        return f"Q: {self.question[:50]}..."

