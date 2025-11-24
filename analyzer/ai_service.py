"""
AI service for generating answers to user questions based on document content.

This module handles communication with Ollama (open-source LLM) to generate contextual answers
based on the uploaded documents.
"""
from django.conf import settings
import ollama
from .models import Document, Chunk


class AIService:
    """
    Service class for interacting with Ollama (open-source language model).
    
    This class handles the generation of answers based on document content
    and user questions using locally running Ollama models.
    """
    
    def __init__(self):
        """Initialize the AI service with Ollama."""
        # Get model name from settings, default to llama3.2 if not specified
        self.model_name = getattr(settings, 'OLLAMA_MODEL', 'llama3.2')
        
        # Test connection to Ollama
        try:
            # Check if Ollama is running by trying to list models
            models = ollama.list()
            # Verify the model exists
            model_names = [m.get('name', m.get('model', '')) for m in models.get('models', [])]
            if self.model_name not in model_names and f"{self.model_name}:latest" not in model_names:
                print(f"Warning: Model '{self.model_name}' not found. Available models: {model_names}")
        except Exception as e:
            raise ValueError(
                f"Ollama is not running or not accessible. "
                f"Please install and start Ollama: https://ollama.ai\n"
                f"Error: {str(e)}"
            )
    
    def generate_answer(self, question, chunks):
        """
        Generate an answer to a question based on relevant document chunks.
        
        Args:
            question: User's question string
            chunks: List of Chunk objects to use as context
            
        Returns:
            tuple: (answer_text, source_chunk_ids)
                - answer_text: Generated answer
                - source_chunk_ids: List of chunk IDs used in the answer
        """
        if not chunks:
            return "No relevant document content found to answer the question.", []
        
        # Build context from chunks with document references
        context_parts = []
        source_chunk_ids = []
        
        for chunk in chunks:
            context_parts.append(
                f"[From {chunk.document.filename}, Chunk {chunk.chunk_index + 1}]\n{chunk.content}"
            )
            source_chunk_ids.append(chunk.id)
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Improved prompt focused on question relevance
        system_prompt = """You are a precise assistant that answers questions based ONLY on the provided document excerpts.
        
CRITICAL INSTRUCTIONS:
1. Answer the question DIRECTLY and SPECIFICALLY using only information from the provided excerpts
2. If the answer is not in the excerpts, say "The provided documents do not contain information to answer this question"
3. Do NOT provide general knowledge or information not found in the excerpts
4. Quote or reference specific parts from the excerpts when possible
5. Be concise and focused on answering exactly what was asked
6. Support multiple languages including English and Korean"""
        
        user_prompt = f"""Question: {question}

Relevant document excerpts:
{context}

Based ONLY on the excerpts above, provide a direct and specific answer to the question. If the answer cannot be found in these excerpts, state that clearly."""
        
        try:
            # Call Ollama API
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options={
                    "temperature": 0.3,  # Lower temperature for more focused answers
                    "num_predict": 1000
                }
            )
            
            answer = response['message']['content'].strip()
            return answer, source_chunk_ids
            
        except Exception as e:
            error_msg = str(e)
            if "model" in error_msg.lower() and "not found" in error_msg.lower():
                return (
                    f"Error: Model '{self.model_name}' not found. "
                    f"Please pull the model first: ollama pull {self.model_name}",
                    source_chunk_ids
                )
            return f"Error generating answer: {error_msg}", source_chunk_ids
    
    def find_relevant_chunks(self, question, all_chunks, limit=10):
        """
        Find the most relevant chunks for a question using keyword matching.
        
        This implementation uses keyword-based relevance. For production,
        consider using vector embeddings and semantic similarity search.
        
        Args:
            question: User's question
            all_chunks: QuerySet of all available chunks
            limit: Maximum number of chunks to return
            
        Returns:
            list: List of Chunk objects, sorted by relevance
        """
        if not all_chunks.exists():
            return []
        
        question_lower = question.lower()
        # Extract meaningful words (longer than 2 characters, not common stop words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom', 'where', 'when', 'why', 'how'}
        question_words = {word for word in question_lower.split() if len(word) > 2 and word not in stop_words}
        
        scored_chunks = []
        for chunk in all_chunks:
            if not chunk.content:
                continue
            
            content_lower = chunk.content.lower()
            # Count matching words and calculate relevance score
            matches = sum(1 for word in question_words if word in content_lower)
            
            # Bonus for exact phrase matches
            if question_lower in content_lower:
                matches += 5
            
            # Bonus for multiple occurrences
            for word in question_words:
                matches += content_lower.count(word) * 0.5
            
            if matches > 0:
                scored_chunks.append((matches, chunk))
        
        # Sort by relevance score and return top chunks
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        relevant_chunks = [chunk for _, chunk in scored_chunks[:limit]]
        
        # If no relevant chunks found, return first few chunks
        if not relevant_chunks:
            relevant_chunks = list(all_chunks[:limit])
        
        return relevant_chunks

