#!/bin/bash

echo "🚀 Setting up Floor Management System - Production Department"
echo "============================================================="

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup PostgreSQL
echo ""
echo "🐘 Setting up PostgreSQL..."
sudo service postgresql start
sudo -u postgres psql -c "CREATE DATABASE floor_management_c;" 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER postgres WITH PASSWORD 'postgres';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "ALTER USER postgres WITH SUPERUSER;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE floor_management_c TO postgres;"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    cat > .env << 'ENVEOF'
# Database Configuration
DB_NAME=floor_management_c
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
SECRET_KEY=django-insecure-codespace-dev-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*.githubpreview.dev

# Security (for production)
# CSRF_TRUSTED_ORIGINS=https://your-domain.com
ENVEOF
    echo "✅ .env file created"
fi

# Run migrations
echo ""
echo "🔄 Running Django migrations..."
python manage.py migrate

# Create cache table
echo ""
echo "📊 Creating cache table..."
python manage.py createcachetable

# Collect static files
echo ""
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "============================================================="
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Run: python manage.py createsuperuser"
echo "  2. Run: python manage.py runserver"
echo "  3. Open browser to forwarded port 8000"
echo ""
echo "🧪 To run the repair workflow tests:"
echo "  python test_repair_workflow.py"
echo ""
echo "============================================================="
