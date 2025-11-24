# Environment Variables Setup

This file documents the required environment variables for the Document Analyzer application.

## Required Variables

Create a `.env` file in the project root with the following variables:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Django Settings
SECRET_KEY=your_django_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## How to Get Values

### OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and paste it as `OPENAI_API_KEY` value

### Django Secret Key

Generate a secure secret key using Python:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it as the `SECRET_KEY` value.

### DEBUG

- Set to `True` for development
- Set to `False` for production

### ALLOWED_HOSTS

- For development: `localhost,127.0.0.1`
- For production: Add your domain name (e.g., `example.com,www.example.com`)

## Security Notes

⚠️ **IMPORTANT**: 
- Never commit the `.env` file to version control
- The `.env` file is already in `.gitignore`
- Keep your API keys secure and never share them
- Rotate keys if they are accidentally exposed

