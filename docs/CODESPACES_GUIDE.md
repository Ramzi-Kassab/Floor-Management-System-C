# GitHub Codespaces Guide

## Why Codespaces for This Project?

Perfect for your incremental migration strategy:

✅ **PostgreSQL pre-configured** - No setup needed
✅ **Claude Code Web compatible** - Can read/write/test everything
✅ **One-click start** - 2-3 minutes to running environment
✅ **No Docker knowledge required** - It just works
✅ **Free tier available** - 120 core-hours/month
✅ **Work from anywhere** - Browser or VS Code

## How to Get Started

### Step 1: Create GitHub Repository

```bash
# In floor_management_system-C folder
git remote add origin https://github.com/YOUR_USERNAME/Floor-Management-System-C.git
git push -u origin master
```

### Step 2: Create Codespace

1. Go to your GitHub repository
2. Click green **Code** button
3. Click **Codespaces** tab
4. Click **Create codespace on master**
5. Wait 2-3 minutes ☕

### Step 3: What Happens Automatically

The setup script (`.devcontainer/setup.sh`) runs:

1. ✅ Creates Python virtual environment
2. ✅ Installs all dependencies from `requirements.txt`
3. ✅ Creates `.env` file with database settings
4. ✅ Waits for PostgreSQL to be ready
5. ✅ Runs Django migrations
6. ✅ Everything ready to use!

### Step 4: Start Working

```bash
# Create admin user (only needed once)
python manage.py createsuperuser

# Start Django server
python manage.py runserver
```

Click the notification popup to open the app in your browser!

## Working with Codespaces

### Running Django Commands

```bash
# Activate venv (usually auto-activated)
source venv/bin/activate

# System check
python manage.py check

# Create migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser
```

### Database Access

PostgreSQL is already running:

```bash
# Connect to PostgreSQL
psql -h db -U postgres -d floor_management_c

# Or use Django dbshell
python manage.py dbshell
```

**Connection details:**
- Host: `db` (in Codespaces) or `localhost` (local)
- Database: `floor_management_c`
- User: `postgres`
- Password: `postgres`

### VS Code Extensions Included

Automatically installed:
- Python (Microsoft)
- Pylance (IntelliSense)
- Black formatter
- Django support
- SQLTools (PostgreSQL management)
- GitHub Copilot (if you have it)

## For Claude Code Web

Claude Code Web can work in your Codespace:

✅ **Read/write files** - Full access to project
✅ **Run commands** - makemigrations, migrate, check, etc.
✅ **Test changes** - Can start server and verify
✅ **Make commits** - Can commit and push changes
✅ **Database access** - Can query and test data

### Workflow with Claude Code Web

1. **You**: Open Codespace
2. **Claude Code Web**: Cleans inventory app from B
3. **You**: Copy to Codespace `apps/inventory/`
4. **Claude Code Web**: Tests migrations, admin, views
5. **Repeat** for next app

## Codespace Management

### Stopping

- Codespace auto-stops after 30 minutes of inactivity
- Or manually: Click your codespace → **Stop codespace**

### Restarting

- Click **Codespaces** → Your codespace → **Open**
- Everything persists (database, files, etc.)

### Deleting

- When done: Delete codespace to free up storage
- Your code is safe in GitHub

### Cost

**Free tier:**
- 120 core-hours/month
- 15 GB storage
- 2-core machine

**Example:**
- 2-core machine = 60 hours/month free
- More than enough for this project!

## Troubleshooting

### PostgreSQL not ready?

Wait a moment, then:
```bash
# Check if PostgreSQL is running
pg_isready -h db -U postgres
```

### Port 8000 already in use?

```bash
# Kill existing server
pkill -f runserver

# Or use different port
python manage.py runserver 0.0.0.0:8001
```

### Migrations not running?

```bash
# Check what's pending
python manage.py showmigrations

# Run specific app
python manage.py migrate inventory
```

## Benefits Summary

| Feature | Local Setup | Codespaces |
|---------|-------------|------------|
| Setup time | 30+ minutes | 3 minutes |
| PostgreSQL config | Manual | Automatic |
| Consistency | Varies by machine | Always same |
| Claude Code Web access | Limited | Full |
| Work from anywhere | No | Yes |
| Cost | Free | Free tier |

## Next Steps

1. ✅ Push project to GitHub
2. ✅ Create Codespace
3. ✅ Verify setup works
4. ✅ Start migrating inventory app
5. ✅ Test thoroughly in Codespace
6. ✅ Repeat for each app

---

**Ready to create your first Codespace?**

Push to GitHub and click that green button! 🚀
