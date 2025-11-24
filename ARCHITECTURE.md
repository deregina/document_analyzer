# Document Analyzer - Architecture Diagram

## System Architecture

```mermaid
graph TB
    subgraph "Client Browser"
        UI[Web Interface]
        Upload[File Upload]
        Question[Question Input]
        Display[Answer Display]
        Sidebar[Source Excerpts Panel]
    end
    
    subgraph "Django Backend"
        Views[Django Views]
        Models[(Database Models)]
        Utils[File Parser Utils]
        AIService[AI Service]
    end
    
    subgraph "Data Storage"
        DB[(SQLite Database)]
        Files[File Storage]
    end
    
    subgraph "AI Processing"
        Ollama[Ollama LLM]
        Chunks[Document Chunks]
    end
    
    UI --> Upload
    UI --> Question
    UI --> Display
    UI --> Sidebar
    
    Upload --> Views
    Question --> Views
    
    Views --> Utils
    Views --> Models
    Views --> AIService
    
    Utils --> Files
    Models --> DB
    
    AIService --> Chunks
    AIService --> Ollama
    
    Chunks --> DB
    Files --> DB
    
    AIService --> Views
    Views --> Display
    Views --> Sidebar
```

## Document Upload Flow

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Django
    participant Parser
    participant Database
    participant FileSystem
    
    User->>Browser: Upload Document (PDF/Word/Excel/Email)
    Browser->>Django: POST /api/upload/
    Django->>Parser: Parse File Content
    Parser->>Django: Return Text Content
    Django->>Database: Save Document Record
    Django->>FileSystem: Save File
    Django->>Parser: Chunk Text (1000 chars, 200 overlap)
    Parser->>Django: Return Chunks
    Django->>Database: Save Chunk Records
    Django->>Browser: Success Response
    Browser->>User: Show Upload Success
```

## Question Answering Flow

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Django
    participant AIService
    participant Database
    participant Ollama
    
    User->>Browser: Enter Question
    Browser->>Django: POST /api/ask/
    Django->>Database: Get All Chunks
    Django->>AIService: Find Relevant Chunks
    AIService->>Database: Query Chunks by Keywords
    Database->>AIService: Return Relevant Chunks
    AIService->>AIService: Score Chunks by Relevance
    AIService->>Django: Return Top Chunks
    Django->>AIService: Generate Answer
    AIService->>Ollama: Send Question + Chunks
    Ollama->>AIService: Return Generated Answer
    AIService->>Django: Return Answer + Chunk IDs
    Django->>Database: Save Q&A + Chunk References
    Django->>Browser: Return Answer + Source Chunks
    Browser->>User: Display Answer & Source Excerpts
```

## Data Model Relationships

```mermaid
erDiagram
    Document ||--o{ Chunk : "has"
    Document ||--o{ QuestionAnswer : "referenced in"
    Conversation ||--o{ QuestionAnswer : "contains"
    QuestionAnswer }o--o{ Chunk : "uses"
    QuestionAnswer }o--o{ Document : "references"
    
    Document {
        int id PK
        string filename
        string file_type
        text parsed_content
        datetime uploaded_at
        int file_size
    }
    
    Chunk {
        int id PK
        int document_id FK
        int chunk_index
        text content
        int start_char
        int end_char
    }
    
    Conversation {
        int id PK
        datetime created_at
        datetime updated_at
    }
    
    QuestionAnswer {
        int id PK
        int conversation_id FK
        text question
        text answer
        datetime created_at
    }
```

## Component Details

### 1. File Upload & Processing
- **Input**: PDF, Word (.docx), Excel (.xlsx), Email (.eml, .msg)
- **Processing**: 
  - Extract text content
  - Split into chunks (1000 chars, 200 char overlap)
  - Store chunks with metadata
- **Output**: Document and Chunk records in database

### 2. Question Processing
- **Input**: User question
- **Processing**:
  - Find relevant chunks using keyword matching
  - Score chunks by relevance (keyword matches, phrase matches)
  - Select top 10 most relevant chunks
- **Output**: List of relevant chunks

### 3. Answer Generation
- **Input**: Question + Relevant Chunks
- **Processing**:
  - Build context from chunks
  - Send to Ollama LLM with focused prompt
  - Generate answer using only provided chunks
- **Output**: Answer + Source chunk IDs

### 4. Display
- **Left Panel**: Question and Answer
- **Right Panel**: Source excerpts (actual chunk text)
- **Features**: Click question to see source excerpts

## Technology Stack

```
┌─────────────────────────────────────────┐
│         Frontend (Browser)              │
│  - HTML/CSS/JavaScript (Vanilla)        │
│  - Drag & Drop File Upload              │
│  - AJAX API Calls                       │
└─────────────────────────────────────────┘
                    ↕ HTTP/REST API
┌─────────────────────────────────────────┐
│         Django Backend                  │
│  - Django 5.0.1                         │
│  - Django REST Framework                │
│  - SQLite Database                      │
│  - File Storage                         │
└─────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────┐
│         File Processing                 │
│  - PyPDF2 (PDF parsing)                │
│  - python-docx (Word parsing)          │
│  - openpyxl (Excel parsing)            │
│  - Email parser (Email parsing)        │
│  - Text chunking utility                │
└─────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────┐
│         AI Service                      │
│  - Ollama Python Client                 │
│  - Chunk Retrieval                      │
│  - Prompt Engineering                   │
│  - Answer Generation                    │
└─────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────┐
│         Ollama LLM                      │
│  - Local LLM (llama3.2)                 │
│  - Runs on local machine                │
│  - No API keys needed                   │
│  - Privacy-focused                      │
└─────────────────────────────────────────┘
```

## Key Features

1. **Chunking System**: Documents split into manageable chunks for better retrieval
2. **Relevance Scoring**: Keyword and phrase matching to find most relevant chunks
3. **Source Attribution**: Shows exact text excerpts used to generate answers
4. **Focused Answers**: LLM instructed to use only provided chunks
5. **Multi-format Support**: Handles PDF, Word, Excel, and Email files
6. **Offline Processing**: All AI processing happens locally via Ollama

## Data Flow Summary

1. **Upload**: File → Parse → Chunk → Store
2. **Question**: Question → Find Chunks → Generate Answer → Display
3. **Display**: Answer + Source Chunks → User Interface

