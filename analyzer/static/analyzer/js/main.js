/**
 * Main JavaScript file for Document Analyzer
 * 
 * This file handles file uploads, question asking, and UI interactions.
 */

// Setup file upload functionality
function setupFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.background = '#f0f2ff';
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.background = '#f8f9ff';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.background = '#f8f9ff';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            uploadFiles(files);
        }
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadFiles(e.target.files);
        }
    });
}

/**
 * Upload files to the server
 * @param {FileList} files - Files to upload
 */
async function uploadFiles(files) {
    const uploadStatus = document.getElementById('uploadStatus');
    
    for (let file of files) {
        const formData = new FormData();
        formData.append('file', file);
        
        uploadStatus.className = 'upload-status';
        uploadStatus.textContent = `Uploading ${file.name}...`;
        uploadStatus.style.display = 'block';
        
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCsrfToken();
            const response = await fetch('/api/upload/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            });
            
            // Check if response is JSON
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                throw new Error(`Server returned HTML instead of JSON. Status: ${response.status}. Response: ${text.substring(0, 200)}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                uploadStatus.className = 'upload-status success';
                uploadStatus.textContent = `✓ ${data.message}`;
                loadDocuments();
            } else {
                uploadStatus.className = 'upload-status error';
                uploadStatus.textContent = `✗ Error: ${data.error}`;
            }
        } catch (error) {
            uploadStatus.className = 'upload-status error';
            let errorMessage = error.message;
            if (error.message.includes('HTML instead of JSON')) {
                errorMessage = 'Server error occurred. Please check the server logs or try again.';
            }
            uploadStatus.textContent = `✗ Upload failed: ${errorMessage}`;
            console.error('Upload error:', error);
        }
    }
}

/**
 * Load and display all documents
 */
async function loadDocuments() {
    try {
        const response = await fetch('/api/documents/');
        const data = await response.json();
        
        const documentsList = document.getElementById('documentsList');
        
        if (data.documents.length === 0) {
            documentsList.innerHTML = '<p class="empty-message">No documents uploaded yet.</p>';
            return;
        }
        
        documentsList.innerHTML = data.documents.map(doc => {
            const icon = getFileIcon(doc.file_type);
            return `
                <div class="document-item" data-doc-id="${doc.id}">
                    <span class="doc-icon">${icon}</span>
                    <span class="doc-name">${escapeHtml(doc.filename)}</span>
                    <span class="doc-type">${doc.file_type.toUpperCase()}</span>
                    <button class="btn-delete" onclick="deleteDocument(${doc.id})" title="Delete">🗑️</button>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading documents:', error);
    }
}

/**
 * Delete a document
 * @param {number} documentId - ID of document to delete
 */
async function deleteDocument(documentId) {
    if (!confirm('Are you sure you want to delete this document?')) {
        return;
    }
    
    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCsrfToken();
        const response = await fetch(`/api/documents/${documentId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadDocuments();
        } else {
            alert('Error deleting document');
        }
    } catch (error) {
        console.error('Error deleting document:', error);
        alert('Error deleting document');
    }
}

/**
 * Ask a question about the documents
 */
async function askQuestion() {
    const questionInput = document.getElementById('questionInput');
    const askButton = document.getElementById('askButton');
    const question = questionInput.value.trim();
    
    if (!question) {
        alert('Please enter a question');
        return;
    }
    
    // Disable button and show loading
    askButton.disabled = true;
    askButton.innerHTML = '<span class="loading"></span> Asking...';
    
    try {
        const requestData = {
            question: question,
            conversation_id: currentConversationId
        };
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCsrfToken();
        const response = await fetch('/api/ask/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(requestData)
        });
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            throw new Error(`Server returned HTML instead of JSON. Status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Update conversation ID
            currentConversationId = data.conversation_id;
            
            // Add Q&A to conversation history
            addQAToHistory(question, data.answer, data.source_chunks);
            
            // Update source chunks panel
            updateSourceChunks(data.source_chunks);
            
            // Clear input
            questionInput.value = '';
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error asking question:', error);
        alert('Error asking question: ' + error.message);
    } finally {
        askButton.disabled = false;
        askButton.textContent = 'Ask';
    }
}

/**
 * Add Q&A pair to conversation history
 * @param {string} question - User's question
 * @param {string} answer - AI's answer
 * @param {Array} sourceChunks - Source chunks used
 */
function addQAToHistory(question, answer, sourceChunks) {
    const history = document.getElementById('conversationHistory');
    
    const qaPair = document.createElement('div');
    qaPair.className = 'qa-pair';
    qaPair.onclick = () => updateSourceChunks(sourceChunks);
    
    qaPair.innerHTML = `
        <div class="question-block">
            <span class="question-label">❓ Question:</span>
            <div class="question-text">${escapeHtml(question)}</div>
        </div>
        <div class="answer-block">
            <span class="answer-label">💡 Answer:</span>
            <div class="answer-text">${escapeHtml(answer)}</div>
        </div>
    `;
    
    history.insertBefore(qaPair, history.firstChild);
}

/**
 * Update the source chunks panel with actual text excerpts
 * @param {Array} sourceChunks - List of source chunks with content
 */
function updateSourceChunks(sourceChunks) {
    const panel = document.getElementById('sourceDocumentsList');
    
    if (!sourceChunks || sourceChunks.length === 0) {
        panel.innerHTML = '<p class="empty-message">No source excerpts for this answer</p>';
        return;
    }
    
    panel.innerHTML = sourceChunks.map(chunk => {
        return `
            <div class="source-chunk-item">
                <div class="source-chunk-header">
                    <span class="source-chunk-doc">📄 ${escapeHtml(chunk.document_name)}</span>
                    <span class="source-chunk-index">Chunk ${chunk.chunk_index + 1}</span>
                </div>
                <div class="source-chunk-content">${escapeHtml(chunk.content)}</div>
            </div>
        `;
    }).join('');
}

/**
 * Get icon for file type
 * @param {string} fileType - Type of file
 * @returns {string} Emoji icon
 */
function getFileIcon(fileType) {
    const icons = {
        'pdf': '📕',
        'docx': '📘',
        'xlsx': '📊',
        'email': '📧',
        'other': '📄'
    };
    return icons[fileType] || icons.other;
}

/**
 * Get CSRF token from cookies
 * @returns {string} CSRF token
 */
function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Allow Enter key to submit question (Shift+Enter for new line)
document.addEventListener('DOMContentLoaded', function() {
    const questionInput = document.getElementById('questionInput');
    if (questionInput) {
        questionInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                askQuestion();
            }
        });
    }
});

