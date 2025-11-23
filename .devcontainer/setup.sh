#!/bin/bash
set -e

echo "🚀 Starting Floor Management System Setup..."

echo "⏳ Waiting for PostgreSQL to be ready..."
until pg_isready -h localhost -p 5432 -U logistics_user; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "✅ PostgreSQL is ready!"

cd /workspaces/Floor-Management-System-C

echo "📦 Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

if [ ! -f .env ]; then
  echo "📝 Creating .env file..."
  cat > .env << 'ENVEOF'
DATABASE_URL=postgresql://logistics_user:logistics_pass@localhost:5432/logistics_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=logistics_db
POSTGRES_USER=logistics_user
POSTGRES_PASSWORD=logistics_pass
DEBUG=True
SECRET_KEY=django-insecure-codespace-development-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,*.githubpreview.dev,*.app.github.dev
STATIC_URL=/static/
STATIC_ROOT=/workspaces/Floor-Management-System-C/staticfiles/
ENVEOF
  echo "✅ .env file created!"
fi

echo "🗄️  Running database migrations..."
python manage.py makemigrations
python manage.py migrate

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "📊 Loading sample data..."
python manage.py load_sample_data || echo "⚠️  Sample data loading skipped"

echo "👤 Creating superuser..."
python manage.py shell << 'PYEOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("✅ Superuser created: username='admin', password='admin123'")
else:
    print("ℹ️  Superuser already exists")
PYEOF

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🎉 Setup Complete! 🎉                             ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  Your Floor Management System is ready to use!            ║"
echo "║                                                            ║"
echo "║  🌐 Application: http://localhost:8000                     ║"
echo "║  🔧 Admin Panel: http://localhost:8000/admin               ║"
echo "║  📊 Inventory:   http://localhost:8000/inventory/          ║"
echo "║  🛒 Purchasing:  http://localhost:8000/purchasing/         ║"
echo "║                                                            ║"
echo "║  👤 Admin Login:                                           ║"
echo "║     Username: admin                                        ║"
echo "║     Password: admin123                                     ║"
echo "║                                                            ║"
echo "║  💡 The server will start automatically!                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
