#!/bin/bash
# Complete setup and run script for Document Analyzer

set -e  # Exit on error

echo "=========================================="
echo "Document Analyzer - Setup Script"
echo "=========================================="
echo ""

# Step 1: Create virtual environment
echo "Step 1: Creating virtual environment..."
python3 -m venv venv

# Step 2: Activate virtual environment
echo "Step 2: Activating virtual environment..."
source venv/bin/activate

# Step 3: Upgrade pip
echo "Step 3: Upgrading pip..."
pip install --upgrade pip --quiet

# Step 4: Install dependencies
echo "Step 4: Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Step 5: Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Step 5: Creating .env file template..."
    SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    cat > .env << EOF
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Django Settings
SECRET_KEY=$SECRET_KEY
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EOF
    echo "✓ .env file created with generated SECRET_KEY"
    echo "⚠ Please edit .env and add your OPENAI_API_KEY"
else
    echo "Step 5: .env file already exists, skipping..."
fi

# Step 6: Run migrations
echo "Step 6: Running database migrations..."
python manage.py makemigrations
python manage.py migrate

echo ""
echo "=========================================="
echo "✓ Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OPENAI_API_KEY"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python manage.py runserver"
echo ""
echo "Or run this script with --run flag to start server immediately:"
echo "  ./install_and_run.sh --run"
echo ""

# Optional: Run server if --run flag is provided
if [ "$1" == "--run" ]; then
    echo "Starting development server..."
    echo "Server will be available at: http://127.0.0.1:8000/"
    echo ""
    python manage.py runserver
fi

