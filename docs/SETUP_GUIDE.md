# Floor Management System C - Setup Guide

## Quick Start

### 1. Create PostgreSQL Database

Using pgAdmin or psql command line:

```sql
CREATE DATABASE floor_management_c;
```

Or using command line:
```bash
createdb floor_management_c
```

### 2. Configure Environment

Create `.env` file from template:
```bash
cp .env.example .env
```

Edit `.env` with your database credentials:
```
DB_NAME=floor_management_c
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
```

### 3. Activate Virtual Environment

```bash
cd D:\PycharmProjects\floor_management_system-C
venv\Scripts\activate
```

### 4. Run Initial Migrations

```bash
python manage.py migrate
```

This will create all Django's default tables.

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit: http://localhost:8000/admin

## Verify Installation

Run system check:
```bash
python manage.py check
```

Should output: `System check identified no issues (0 silenced).`

## Next Steps - Adding Inventory App

When Claude Code Web provides the cleaned inventory app:

1. Create the app:
   ```bash
   python manage.py startapp inventory apps/inventory
   ```

2. Copy models from cleaned version

3. Add to INSTALLED_APPS in `settings.py`:
   ```python
   'apps.inventory',
   ```

4. Create migrations:
   ```bash
   python manage.py makemigrations inventory
   python manage.py migrate
   ```

5. Register models in admin

6. Test thoroughly before proceeding to next app

## Troubleshooting

### Database Connection Error
- Check PostgreSQL is running
- Verify `.env` credentials
- Ensure database `floor_management_c` exists

### Migration Issues
- Check all models have `app_label` set correctly
- Verify no circular dependencies
- Use `python manage.py showmigrations` to see status

### Import Errors
- Ensure virtual environment is activated
- Check all dependencies installed: `pip list`
- Verify app is in INSTALLED_APPS

## Creating New GitHub Repository

To push this project to GitHub:

1. Create new repository on GitHub (e.g., `Floor-Management-System-C`)

2. Add remote:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/Floor-Management-System-C.git
   ```

3. Push to GitHub:
   ```bash
   git push -u origin master
   ```

## Current Status

✅ Clean Django project created
✅ PostgreSQL configured
✅ Virtual environment set up
✅ Dependencies installed
✅ System check passes (0 errors)
⏳ Ready for inventory app migration

See `docs/migration_log.md` for detailed progress tracking.
