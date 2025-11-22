# Floor Management System - Clean Build (Version C)

A comprehensive Django-based management system for drilling bit production and repair operations.

## Project Overview

This is a clean refactored version of the Floor Management System, built incrementally with proper architecture and thorough testing at each step.

### Key Features
- **Inventory Management:** BitDesign, BOM, Items tracking
- **Operations:** Work Orders, Job Cards, Process routing
- **HR Management:** User availability, KPIs, qualifications
- **QC & NDT:** Quality control and non-destructive testing workflows

## Technology Stack

- **Framework:** Django 5.2.6
- **Database:** PostgreSQL
- **API:** Django REST Framework
- **Python:** 3.10+

## Project Structure

```
floor_management_system-C/
├── apps/                    # Django applications
│   ├── inventory/           # Core inventory models
│   ├── operations/          # Work orders & job cards
│   └── hr/                  # HR management
├── floor_project/           # Project settings
├── static/                  # Static files (CSS, JS, images)
├── media/                   # User uploads
├── templates/               # Global templates
├── docs/                    # Documentation
│   └── migration_log.md     # Detailed migration tracking
└── venv/                    # Virtual environment
```

## Setup Instructions

### 1. Clone and Navigate
```bash
cd D:\PycharmProjects\floor_management_system-C
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Copy `.env.example` to `.env` and update with your settings:
```bash
cp .env.example .env
```

Edit `.env`:
```
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=floor_management_c
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Create Database
```bash
# Using psql or pgAdmin
createdb floor_management_c
```

### 6. Run Migrations
```bash
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
```

### 8. Run Development Server
```bash
python manage.py runserver
```

Visit: http://localhost:8000/admin

## Development Workflow

### Adding New Apps

1. Create app in `apps/` directory
2. Add to `INSTALLED_APPS` in settings.py
3. Create models with explicit `app_label`
4. Run `makemigrations` and `migrate`
5. Test thoroughly before proceeding
6. Update `docs/migration_log.md`

### Testing Protocol

Before committing changes:
```bash
python manage.py check              # Django system check
python manage.py makemigrations     # Check for model changes
python manage.py migrate            # Apply migrations
python manage.py test               # Run tests
```

## Migration from Version B

This is a **clean build**, not a direct migration. Apps are being moved incrementally:

1. ✅ Project setup complete
2. ⏳ Inventory app (in progress)
3. ⏳ Operations app (pending)
4. ⏳ HR app (pending)

See `docs/migration_log.md` for detailed progress.

## Key Decisions

- **PostgreSQL:** Production-ready database from the start
- **Incremental Migration:** One app at a time with thorough testing
- **Clean Architecture:** Proper app organization under `apps/`
- **Environment Config:** Using python-decouple for flexibility

## Dependencies

- Django 5.2.6
- djangorestframework 3.15.2
- psycopg2-binary 2.9.10
- python-decouple 3.8
- Pillow 10.4.0
- qrcode 8.0
- django-widget-tweaks 1.5.0
- django-ratelimit 4.1.0

## Documentation

- `docs/migration_log.md` - Detailed migration tracking and decisions
- `docs/` - Additional documentation as project grows

## Contributing

1. Always activate virtual environment
2. Create feature branches from master
3. Test thoroughly before committing
4. Update migration log with changes
5. Follow Django best practices

## Safety Notes

- `floor_management_system-B` remains untouched as reference
- Each app migration is a separate commit
- Fresh database means easy rollback
- Test at each step before proceeding

## Status

**Current Phase:** Initial Setup Complete
**Next Step:** Create and test inventory app

---

**Created:** 2025-11-22
**Last Updated:** 2025-11-22
