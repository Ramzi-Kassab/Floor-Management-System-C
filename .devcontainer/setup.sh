#!/bin/bash
set -e  # Exit on error

# This script runs automatically when Codespace is created

echo "🚀 Setting up Floor Management System..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv
source venv/bin/activate

# Verify venv activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated: $VIRTUAL_ENV"

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo "✅ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << EOL
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=floor_management_c
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
EOL
fi

# Wait for PostgreSQL to be ready (with timeout)
echo "⏳ Waiting for PostgreSQL (max 60 seconds)..."
COUNTER=0
until PGPASSWORD=postgres psql -h db -U postgres -c '\q' 2>/dev/null; do
  COUNTER=$((COUNTER+1))
  if [ $COUNTER -gt 60 ]; then
    echo "❌ PostgreSQL failed to start within 60 seconds"
    echo "💡 Try running setup manually: bash .devcontainer/setup.sh"
    exit 1
  fi
  echo "   ... attempt $COUNTER/60"
  sleep 1
done

echo "✅ PostgreSQL is ready!"

# Run Django system check
echo "🔍 Running Django system check..."
python manage.py check

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate

# Create cache table
echo "📊 Creating cache table..."
python manage.py createcachetable 2>/dev/null || echo "⚠️  Cache table already exists or not needed"

# Collect static files (quietly, for Codespaces)
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear --quiet 2>/dev/null || echo "⚠️  Static files collection skipped"

# Create necessary directories
echo "📁 Creating media directories..."
mkdir -p media/uploads media/qrcodes media/reports 2>/dev/null || true

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Setup complete! System is ready to use."
echo ""
echo "🎯 Quick Start:"
echo "  1. Create admin user:  python manage.py createsuperuser"
echo "  2. Start server:       ./start.sh"
echo "     OR manually:        python manage.py runserver 0.0.0.0:8000"
echo ""
echo "🌐 Access URLs (when server is running):"
echo "  - Home:    Click the 'Open in Browser' popup"
echo "  - Admin:   Add /admin/ to the URL"
echo ""
echo "📝 Useful commands:"
echo "  - Activate venv:       source venv/bin/activate"
echo "  - Django shell:        python manage.py shell"
echo "  - Check status:        python manage.py check"
echo "  - View migrations:     python manage.py showmigrations"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
