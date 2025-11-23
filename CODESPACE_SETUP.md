# Codespace Setup - Quick Reference

## Database Credentials

```
Database: floor_management_c
User: postgres
Password: postgres
Host: localhost
Port: 5432
```

## Quick Start Commands

```bash
# Start PostgreSQL
sudo service postgresql start

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python test_repair_workflow.py

# Start server
python manage.py runserver
```

## URLs

- **Home**: http://localhost:8000/
- **Admin**: http://localhost:8000/admin/
- **Login**: http://localhost:8000/accounts/login/
- **Production**: http://localhost:8000/production/

## Branch Name

```
claude/create-production-department-01GGfP6mxzwRoRUKtaE66GbR
```

---

## Agent Prompt for Codespace Setup

Use this prompt to share with other agents:

```
Setup GitHub Codespace for Floor Management System - Production Department:

BRANCH: claude/create-production-department-01GGfP6mxzwRoRUKtaE66GbR

CREDENTIALS:
- Database: floor_management_c
- User: postgres  
- Password: postgres
- Host: localhost:5432

SETUP STEPS:
1. Install PostgreSQL: sudo apt-get update && sudo apt-get install -y postgresql postgresql-contrib libpq-dev
2. Start PostgreSQL: sudo service postgresql start
3. Install Python deps: pip install -r requirements.txt
4. Run migrations: python manage.py migrate
5. Create superuser: python manage.py createsuperuser
6. Start server: python manage.py runserver

TESTING:
- Backend tests: python test_repair_workflow.py
- All 13 tests should pass
- Test results in TEST_RESULTS.md

FEATURES READY:
- BOM management with variance tracking
- Cutter layout grid (180 positions)  
- Repair history with audit trail
- Work order management (NEW/REPAIR)
- BitInstance serial tracking

PORT FORWARDING:
- 8000: Django dev server
- 5432: PostgreSQL

The system is production-ready. All migrations (0007, 0008) are applied.
Home page fixed for UTF-8 encoding to support Arabic language.
```

---

## Troubleshooting

### PostgreSQL won't start
```bash
sudo service postgresql status
sudo service postgresql start
```

### Unicode errors
- All files use UTF-8 encoding
- Django settings have DEFAULT_CHARSET='utf-8'
- Arabic language support enabled

### Port already in use
```bash
# Kill process on port 8000
sudo lsof -ti:8000 | xargs kill -9

# Or use different port
python manage.py runserver 8001
```

### Database connection failed
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Recreate database
sudo -u postgres psql -c "DROP DATABASE floor_management_c;"
sudo -u postgres psql -c "CREATE DATABASE floor_management_c;"
python manage.py migrate
```

---

## What's Included

✅ Complete repair workflow backend
✅ BOM management models
✅ Cutter layout grid system  
✅ Repair history tracking
✅ Work order management
✅ UTF-8 encoding support
✅ Arabic language support
✅ Comprehensive test suite (13/13 passing)
✅ Production-ready migrations

---

## Files Modified in This Session

1. `.devcontainer/devcontainer.json` - Removed problematic postgres-asdf feature
2. `.devcontainer/setup.sh` - Added PostgreSQL apt-get installation
3. `production/views_home.py` - New home view with UTF-8
4. `production/templates/production/home.html` - Welcome page
5. `floor_project/urls.py` - Added root URL
6. `floor_project/settings.py` - Added UTF-8 charset settings

---

**Last Updated**: 2025-11-23
**Commit**: 6cfacdb
