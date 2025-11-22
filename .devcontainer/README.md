# Codespaces Setup

## What This Does

When you create a GitHub Codespace for this project:

1. ✅ **Python 3.10** installed and configured
2. ✅ **PostgreSQL 15** running automatically
3. ✅ **All dependencies** installed (Django, etc.)
4. ✅ **Database created** (floor_management_c)
5. ✅ **Migrations run** automatically
6. ✅ **VS Code extensions** for Django development
7. ✅ **Ports forwarded** (8000 for Django, 5432 for PostgreSQL)

## How to Use

### Create Codespace
1. Push this project to GitHub
2. Go to your repository
3. Click **Code** → **Codespaces** → **Create codespace on master**
4. Wait 2-3 minutes for setup

### Once Codespace Opens

Everything is ready! Just:

```bash
# Activate virtual environment (if not auto-activated)
source venv/bin/activate

# Create admin user
python manage.py createsuperuser

# Start Django
python manage.py runserver
```

Click the popup to open the app in your browser!

### Database Connection

PostgreSQL is already running and connected:
- **Host**: db (internal container name)
- **Database**: floor_management_c
- **User**: postgres
- **Password**: postgres

### For Claude Code Web

Claude Code Web can:
- Read and write all files
- Run Django commands (makemigrations, migrate, check)
- Start/stop the server
- Access the database
- Make commits and push

This makes incremental app migration super smooth!

## No Docker Knowledge Required

You don't need Docker installed on your local machine. GitHub Codespaces handles everything in the cloud.

## Benefits

- ✅ Consistent environment (no "works on my machine")
- ✅ PostgreSQL already configured
- ✅ No local setup needed
- ✅ Works from any computer (even Chromebook)
- ✅ Free tier: 120 core-hours/month
