#!/bin/bash

# This script runs automatically when Codespace is created

echo "🚀 Setting up Floor Management System..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

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

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
until PGPASSWORD=postgres psql -h db -U postgres -c '\q' 2>/dev/null; do
  sleep 1
done

echo "✅ PostgreSQL is ready!"

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate

echo "✨ Setup complete! Run 'python manage.py createsuperuser' to create an admin account."
echo "🌐 Start server with: python manage.py runserver"
