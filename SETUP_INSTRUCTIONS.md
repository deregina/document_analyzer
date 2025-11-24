# Quick Setup Instructions

Follow these steps to get the Document Analyzer up and running:

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment

1. Create a `.env` file in the project root
2. Copy the template below and fill in your values:

```env
OPENAI_API_KEY=your_key_here
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

To generate a Django secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Step 3: Initialize Database

```bash
python manage.py makemigrations
python manage.py migrate
```

## Step 4: (Optional) Create Admin User

```bash
python manage.py createsuperuser
```

## Step 5: Run Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## Troubleshooting

- **Import errors**: Make sure virtual environment is activated
- **Database errors**: Run migrations again
- **API errors**: Check that OPENAI_API_KEY is set correctly
- **Static files not loading**: Run `python manage.py collectstatic` (for production)

For detailed information, see README.md

