# Document Analyzer Web Application

A Django-based web application that allows users to upload documents (PDF, Word, Excel, Email) and ask questions about them using AI-powered analysis. The application supports multiple languages including English and Korean.

## Features

- 📄 **Multi-format Support**: Upload and analyze PDF, Word (.docx), Excel (.xlsx), and Email (.eml, .msg) files
- 🌍 **Multi-language Support**: Handles documents in English, Korean, and other languages
- 💾 **Persistent Storage**: Documents are saved so you don't need to re-upload them
- 🤖 **AI-Powered Q&A**: Ask questions about your documents and get intelligent answers
- 📚 **Source Document Tracking**: See which documents were used to generate each answer
- 🎨 **Modern UI**: Clean, responsive interface with drag-and-drop file upload

## Technology Stack

- **Backend**: Django 5.0.1
- **AI Integration**: Ollama (open-source LLM) - runs locally, free, no API keys needed
- **File Parsing**: 
  - PyPDF2 for PDF files
  - python-docx for Word documents
  - openpyxl for Excel spreadsheets
  - email parser for email files
- **Frontend**: HTML, CSS, JavaScript (vanilla)

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- **Ollama** (open-source LLM - recommended, free) OR OpenAI API key
  - Install Ollama: https://ollama.ai (see [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for details)
  - Or get OpenAI API key: https://platform.openai.com/api-keys

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd side
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root directory:

```bash
# AI Model Configuration (choose one):
# Option 1: Use Ollama (open-source, free, runs locally)
# No API key needed! Just install Ollama and download a model.
# See OLLAMA_SETUP.md for instructions.

# Option 2: Use OpenAI API (requires API key and credits)
# OPENAI_API_KEY=your_openai_api_key_here

# Ollama Model (optional, defaults to llama3.2)
# OLLAMA_MODEL=llama3.2

# Django Settings
SECRET_KEY=your_django_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Important**: 
- **Recommended**: Use Ollama (free, open-source). See [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for setup.
- **Alternative**: Use OpenAI API (requires API key and credits)
- Generate a Django secret key using: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- Never commit the `.env` file to version control (it's already in `.gitignore`)

### 5. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)

To access the Django admin interface:

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Usage

### Uploading Documents

1. Click on the upload area or drag and drop files
2. Supported formats: PDF, Word (.docx), Excel (.xlsx), Email (.eml, .msg)
3. Files are automatically parsed and stored
4. Uploaded documents appear in the "Uploaded Documents" section

### Asking Questions

1. Type your question in the question input area
2. Click "Ask" or press Enter (Shift+Enter for new line)
3. The AI will analyze your documents and provide an answer
4. Source documents used for the answer appear in the right sidebar

### Managing Documents

- View all uploaded documents in the documents list
- Delete documents by clicking the delete button (🗑️)
- Documents persist across sessions

## Project Structure

```
side/
├── analyzer/                 # Main application
│   ├── models.py            # Database models (Document, Conversation, QuestionAnswer)
│   ├── views.py             # View functions
│   ├── urls.py              # URL routing
│   ├── utils.py             # File parsing utilities
│   ├── ai_service.py        # OpenAI API integration
│   ├── admin.py             # Django admin configuration
│   └── static/              # Static files (CSS, JS)
├── docanalyzer/             # Django project settings
│   ├── settings.py          # Project configuration
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI configuration
├── templates/               # HTML templates
│   ├── base.html           # Base template
│   └── analyzer/           # App-specific templates
├── uploads/                 # Uploaded files storage
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## API Endpoints

- `GET /` - Main page
- `POST /api/upload/` - Upload a file
- `POST /api/ask/` - Ask a question
- `GET /api/documents/` - List all documents
- `GET /api/conversation/<id>/` - Get conversation history
- `DELETE /api/documents/<id>/delete/` - Delete a document

## Security Considerations

1. **API Keys**: Never commit API keys or secrets to version control
2. **Environment Variables**: Use `.env` file for sensitive configuration
3. **File Upload**: The application validates file types and sizes
4. **CSRF Protection**: Django's CSRF protection is enabled
5. **Production**: Set `DEBUG=False` and configure `ALLOWED_HOSTS` for production

## Troubleshooting

### File Upload Issues

- Ensure file size is under 50MB
- Check that file format is supported (PDF, DOCX, XLSX, EML, MSG)
- Verify file is not corrupted

### AI Answer Issues

- Check that `OPENAI_API_KEY` is set correctly in `.env`
- Verify you have sufficient OpenAI API credits
- Ensure documents have been parsed successfully (check parsed_content in admin)

### Database Issues

- Run migrations: `python manage.py migrate`
- Check database file permissions

## Development

### Running Tests

```bash
python manage.py test
```

### Accessing Admin Panel

1. Create superuser: `python manage.py createsuperuser`
2. Visit: `http://127.0.0.1:8000/admin/`
3. Login with superuser credentials

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and modular

## Future Enhancements

- [ ] Vector embeddings for better document search
- [ ] Support for more file formats (PowerPoint, images with OCR)
- [ ] User authentication and document sharing
- [ ] Export conversation history
- [ ] Batch file upload
- [ ] Document preview functionality
- [ ] Advanced search within documents

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please open an issue on the GitHub repository.

## Acknowledgments

- Django framework
- OpenAI for AI capabilities
- All open-source libraries used in this project

