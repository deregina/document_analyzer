"""
Views for the document analyzer application.

This module contains all the view functions for handling file uploads,
displaying documents, and processing questions.
"""
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import Document, Conversation, QuestionAnswer, Chunk
from .utils import parse_file, detect_language, chunk_text
from .ai_service import AIService
import json


def index(request):
    """
    Main page view - displays file upload form and existing documents.
    
    Returns:
        HttpResponse: Rendered template with documents list
    """
    documents = Document.objects.all()
    conversations = Conversation.objects.all()
    
    context = {
        'documents': documents,
        'conversations': conversations,
    }
    return render(request, 'analyzer/index.html', context)


@require_http_methods(["POST"])
def upload_file(request):
    """
    Handle file upload and parsing.
    
    Expected POST data:
        - file: The uploaded file
        
    Returns:
        JsonResponse: Success status and document info
    """
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        uploaded_file = request.FILES['file']
        
        # Determine file type
        filename = uploaded_file.name.lower()
        if filename.endswith('.pdf'):
            file_type = 'pdf'
        elif filename.endswith('.docx'):
            file_type = 'docx'
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_type = 'xlsx'
        elif filename.endswith('.eml') or filename.endswith('.msg'):
            file_type = 'email'
        else:
            return JsonResponse({'error': 'Unsupported file type'}, status=400)
        
        # Check if file with same name already exists
        existing_doc = Document.objects.filter(filename=uploaded_file.name).first()
        if existing_doc:
            return JsonResponse({
                'success': True,
                'message': 'File already exists',
                'document_id': existing_doc.id,
                'filename': existing_doc.filename
            })
        
        # Save the file
        document = Document(
            filename=uploaded_file.name,
            file_type=file_type,
            file_size=uploaded_file.size
        )
        document.file = uploaded_file
        document.save()
        
        # Parse the file content and create chunks
        try:
            file_path = document.file.path
            parsed_content = parse_file(file_path, file_type)
            document.parsed_content = parsed_content
            document.save()
            
            # Create chunks from the parsed content
            if parsed_content and len(parsed_content.strip()) > 0:
                chunks = chunk_text(parsed_content, chunk_size=1000, chunk_overlap=200)
                for idx, (chunk_content, start_char, end_char) in enumerate(chunks):
                    Chunk.objects.create(
                        document=document,
                        chunk_index=idx,
                        content=chunk_content,
                        start_char=start_char,
                        end_char=end_char
                    )
        except Exception as e:
            # Log the error but don't fail the upload
            import traceback
            print(f"Error parsing file {uploaded_file.name}: {str(e)}")
            print(traceback.format_exc())
            document.parsed_content = f"Error parsing file: {str(e)}"
            document.save()
        
        return JsonResponse({
            'success': True,
            'message': 'File uploaded and parsed successfully',
            'document_id': document.id,
            'filename': document.filename,
            'file_type': document.file_type
        })
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Upload error: {error_msg}")
        print(traceback.format_exc())
        return JsonResponse({'error': f'Upload failed: {error_msg}'}, status=500)


@require_http_methods(["POST"])
def ask_question(request):
    """
    Handle user questions and generate answers using AI.
    
    Expected POST data:
        - question: User's question
        - conversation_id: Optional conversation ID (for continuing conversation)
        - document_ids: Optional list of document IDs to use (if not provided, uses all)
        
    Returns:
        JsonResponse: Answer and source document information
    """
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        
        if not question:
            return JsonResponse({'error': 'Question is required'}, status=400)
        
        # Get or create conversation
        conversation_id = data.get('conversation_id')
        if conversation_id:
            conversation = get_object_or_404(Conversation, id=conversation_id)
        else:
            conversation = Conversation.objects.create()
        
        # Get documents to search (if specified, otherwise search all)
        document_ids = data.get('document_ids', [])
        if document_ids:
            all_chunks = Chunk.objects.filter(document_id__in=document_ids)
        else:
            all_chunks = Chunk.objects.all()
        
        if not all_chunks.exists():
            return JsonResponse({'error': 'No document chunks available. Please upload documents first.'}, status=400)
        
        # Initialize AI service and generate answer
        try:
            ai_service = AIService()
            # Find relevant chunks based on the question
            relevant_chunks = ai_service.find_relevant_chunks(question, all_chunks, limit=10)
            # Generate answer using relevant chunks
            answer, source_chunk_ids = ai_service.generate_answer(question, relevant_chunks)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=500)
        except Exception as e:
            return JsonResponse({'error': f'AI service error: {str(e)}'}, status=500)
        
        # Save Q&A pair
        qa = QuestionAnswer.objects.create(
            conversation=conversation,
            question=question,
            answer=answer
        )
        
        # Add source chunks and documents
        if source_chunk_ids:
            source_chunks = Chunk.objects.filter(id__in=source_chunk_ids)
            qa.source_chunks.set(source_chunks)
            # Also add the parent documents
            source_docs = Document.objects.filter(chunks__id__in=source_chunk_ids).distinct()
            qa.source_documents.set(source_docs)
        
        # Get source chunk info for response (showing actual text)
        source_chunks_info = [
            {
                'id': chunk.id,
                'document_name': chunk.document.filename,
                'chunk_index': chunk.chunk_index,
                'content': chunk.content,
                'preview': chunk.content[:200] + '...' if len(chunk.content) > 200 else chunk.content
            }
            for chunk in qa.source_chunks.all()
        ]
        
        return JsonResponse({
            'success': True,
            'answer': answer,
            'conversation_id': conversation.id,
            'qa_id': qa.id,
            'source_chunks': source_chunks_info
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_conversation(request, conversation_id):
    """
    Get all Q&A pairs for a conversation.
    
    Args:
        conversation_id: ID of the conversation
        
    Returns:
        JsonResponse: List of Q&A pairs with source documents
    """
    conversation = get_object_or_404(Conversation, id=conversation_id)
    qa_pairs = conversation.qa_pairs.all()
    
    qa_data = []
    for qa in qa_pairs:
        qa_data.append({
            'id': qa.id,
            'question': qa.question,
            'answer': qa.answer,
            'created_at': qa.created_at.isoformat(),
            'source_chunks': [
                {
                    'id': chunk.id,
                    'document_name': chunk.document.filename,
                    'chunk_index': chunk.chunk_index,
                    'content': chunk.content,
                    'preview': chunk.content[:200] + '...' if len(chunk.content) > 200 else chunk.content
                }
                for chunk in qa.source_chunks.all()
            ]
        })
    
    return JsonResponse({
        'conversation_id': conversation.id,
        'qa_pairs': qa_data
    })


@require_http_methods(["DELETE"])
def delete_document(request, document_id):
    """
    Delete a document.
    
    Args:
        document_id: ID of the document to delete
        
    Returns:
        JsonResponse: Success status
    """
    document = get_object_or_404(Document, id=document_id)
    document.delete()
    return JsonResponse({'success': True, 'message': 'Document deleted'})


@require_http_methods(["GET"])
def list_documents(request):
    """
    Get list of all uploaded documents.
    
    Returns:
        JsonResponse: List of documents
    """
    documents = Document.objects.all()
    doc_data = [
        {
            'id': doc.id,
            'filename': doc.filename,
            'file_type': doc.file_type,
            'uploaded_at': doc.uploaded_at.isoformat(),
            'file_size': doc.file_size
        }
        for doc in documents
    ]
    
    return JsonResponse({'documents': doc_data})

