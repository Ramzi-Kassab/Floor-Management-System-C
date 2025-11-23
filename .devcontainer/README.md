# GitHub Codespaces Setup

This directory contains the configuration for GitHub Codespaces development environment.

## What's Included

### Automatic Setup
When you create a Codespace, the following is automatically configured:

- ✅ Python 3.11
- ✅ Node.js 18
- ✅ PostgreSQL 16
- ✅ All Python dependencies from requirements.txt
- ✅ VS Code extensions for Django development
- ✅ Database created and migrations applied
- ✅ Environment variables configured

### VS Code Extensions
- Python
- Pylance (Python language server)
- Black formatter
- Django template support
- Jinja template support
- SQL Tools with PostgreSQL driver

### Port Forwarding
- **8000**: Django development server
- **5432**: PostgreSQL database

## Quick Start

Once your Codespace is created:

1. **Create a superuser** (for Django admin):
   ```bash
   python manage.py createsuperuser
   ```

2. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

3. **Access the application**:
   - Click on the "Ports" tab in VS Code
   - Click the globe icon next to port 8000
   - Or use the popup notification

## Testing

### Run the Repair Workflow Tests
```bash
python test_repair_workflow.py
```

This will test all the production department repair workflow features:
- BOM management
- Cutter layout grid
- Repair history tracking
- Work order management

### Run Django Tests
```bash
python manage.py test
```

## Database Access

The PostgreSQL database is automatically configured:

- **Database**: floor_management_c
- **User**: postgres
- **Password**: postgres
- **Host**: localhost
- **Port**: 5432

### Access via psql
```bash
sudo -u postgres psql floor_management_c
```

### Access via SQL Tools Extension
1. Open SQL Tools extension in VS Code
2. Use the pre-configured PostgreSQL connection
3. Browse tables and run queries

## Environment Variables

Environment variables are configured in `.env` file (auto-created):

```
DB_NAME=floor_management_c
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=django-insecure-codespace-dev-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*.githubpreview.dev
```

## Useful Commands

### Django Management
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell

# Run server
python manage.py runserver
```

### Database Management
```bash
# Check migration status
python manage.py showmigrations

# Run specific migration
python manage.py migrate production 0007

# Reset database (careful!)
python manage.py flush
```

### Development
```bash
# Format code with Black
black .

# Check code
python manage.py check

# Run tests
python manage.py test production
```

## Troubleshooting

### PostgreSQL not running
```bash
sudo service postgresql start
```

### Reset database
```bash
sudo -u postgres psql -c "DROP DATABASE floor_management_c;"
sudo -u postgres psql -c "CREATE DATABASE floor_management_c;"
python manage.py migrate
```

### Reinstall dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

## Production Department Features

This branch includes the complete repair workflow backend:

### Models
- **BitDesign** & **BitDesignRevision**: Design blueprints
- **BOMItem** & **ActualBOM**: Bill of materials tracking
- **CutterLayoutPosition**: 3D cutter layout grid
- **ActualCutterInstallation**: Installation tracking
- **BitInstance**: Physical bit tracking
- **WorkOrder**: Manufacturing and repair orders
- **RepairHistory**: Complete repair audit trail

### Migrations
- `0007_add_bom_and_repair_history_models`
- `0008_add_cutter_layout_management`

### Test Suite
Run `python test_repair_workflow.py` to verify all functionality.

## Support

For issues or questions, refer to:
- `TEST_RESULTS.md`: Comprehensive test report
- `TESTING_COMPLETE.md`: Executive summary
- Django documentation: https://docs.djangoproject.com/
