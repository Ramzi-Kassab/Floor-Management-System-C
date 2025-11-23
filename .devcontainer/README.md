# GitHub Codespaces Configuration

This directory contains the configuration for GitHub Codespaces to automatically set up your development environment.

## What Gets Installed

### Services
- **PostgreSQL 15** - Production database
- **Python 3.11** - Application runtime
- **Node.js 18** - For frontend tooling

### VS Code Extensions
- Python (with Pylance)
- Django support
- Jinja template syntax
- Docker support
- GitLens
- Black formatter
- ESLint & Prettier

## Automatic Setup

When you create a Codespace, it will automatically:

1. ✅ Start PostgreSQL database
2. ✅ Install Python dependencies
3. ✅ Create `.env` file with database credentials
4. ✅ Run database migrations
5. ✅ Collect static files
6. ✅ Load sample data
7. ✅ Create admin superuser
8. ✅ Start Django development server

## Access Information

### Application URLs
- **Main App**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Inventory**: http://localhost:8000/inventory/
- **Purchasing**: http://localhost:8000/purchasing/
- **REST API**: http://localhost:8000/api/inventory/

### Default Credentials
```
Username: admin
Password: admin123
```

### Database Connection
```
Host: localhost
Port: 5432
Database: logistics_db
User: logistics_user
Password: logistics_pass
```

## Manual Commands

If you need to run commands manually:

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data
python manage.py load_sample_data

# Start development server
python manage.py runserver 0.0.0.0:8000

# Access Django shell
python manage.py shell

# Run tests
python manage.py test
```

## Files

- **devcontainer.json** - Main configuration
- **docker-compose.yml** - Services definition (app + PostgreSQL)
- **Dockerfile** - Custom Python image with dependencies
- **setup.sh** - Post-create setup script

## Features

### VS Code Settings
- Auto-formatting with Black
- Linting with Pylint
- Django template support
- Git integration

### Port Forwarding
- Port 8000: Django application (auto-forwarded)
- Port 5432: PostgreSQL (silent forwarding)

### Environment Variables
All necessary environment variables are automatically configured in the container.

## Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432 -U logistics_user

# Restart PostgreSQL
sudo service postgresql restart
```

### Server Not Starting
```bash
# Check for port conflicts
lsof -i :8000

# Manually start server
python manage.py runserver 0.0.0.0:8000
```

### Reset Everything
```bash
# Drop and recreate database
python manage.py flush
python manage.py migrate
python manage.py load_sample_data
```

## Development Workflow

1. **Create Codespace** from your branch
2. **Wait for setup** (2-3 minutes)
3. **Open forwarded port 8000** in browser
4. **Login** with admin credentials
5. **Start developing!**

The server runs automatically and will reload on code changes.
