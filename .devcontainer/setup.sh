#!/bin/bash
echo "🚀 Setting up Floor Management System - Production Department"
echo "============================================================="

# Install Python dependencies (no sudo needed)
echo ""
echo "📦 Installing Python dependencies..."
pip install --upgrade pip --break-system-packages
pip install -r requirements.txt --break-system-packages

# Setup PostgreSQL (user-level, no sudo)
echo ""
echo "🐘 Setting up PostgreSQL (user-level)..."

# Create PostgreSQL directories
mkdir -p ~/postgres/data ~/postgres/socket

# Check if already initialized
if [ ! -f ~/postgres/data/PG_VERSION ]; then
    echo "Initializing PostgreSQL database..."
    initdb -D ~/postgres/data
    echo "unix_socket_directories = '/home/vscode/postgres/socket'" >> ~/postgres/data/postgresql.conf
fi

# Start PostgreSQL
echo "Starting PostgreSQL..."
pg_ctl -D ~/postgres/data -l ~/postgres/logfile start

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 3

# Create database and user
echo "Creating database and user..."
psql -d postgres -c "CREATE USER postgres WITH SUPERUSER PASSWORD 'postgres';" 2>/dev/null || echo "✓ User already exists"
psql -d postgres -c "CREATE DATABASE floor_management_c OWNER postgres;" 2>/dev/null || echo "✓ Database already exists"

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
python manage.py createcachetable 2>/dev/null || echo "✓ Cache table exists"

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
echo "  2. Run: python manage.py runserver 0.0.0.0:8000"
echo "  3. Access via PORTS tab → click 🌐 icon"
echo ""
echo "🧪 To run the repair workflow tests:"
echo "  python test_repair_workflow.py"
echo ""
echo "============================================================="
