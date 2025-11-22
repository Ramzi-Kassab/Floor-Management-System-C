# Codespaces Testing Guide

## 🎯 Quick Start in Codespaces

This project is **fully configured** for GitHub Codespaces with automated setup. Follow these steps to start testing:

### Step 1: Create Codespace (If Not Already Created)

1. Go to your GitHub repository
2. Click **Code** → **Codespaces** → **Create codespace on your branch**
3. Wait 2-3 minutes for automatic setup ☕

### Step 2: Post-Setup (First Time Only)

After Codespace opens, the setup script runs automatically. You'll see:

```
🚀 Setting up Floor Management System...
📦 Creating virtual environment...
✅ Virtual environment activated
📚 Installing dependencies...
✅ Dependencies installed
⏳ Waiting for PostgreSQL...
✅ PostgreSQL is ready!
🔍 Running Django system check...
🔄 Running migrations...
✨ Setup complete!
```

**Create your admin user:**
```bash
source venv/bin/activate
python manage.py createsuperuser
```

### Step 3: Start the Server

**Option A: Quick Start (Recommended)**
```bash
./start.sh
```

**Option B: Manual Start**
```bash
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### Step 4: Access in Browser

1. VS Code will show a popup: **"Your application running on port 8000 is available"**
2. Click **"Open in Browser"**
3. You'll see the Floor Management System home page! 🎉

**URLs:**
- **Home Page:** `https://{your-codespace}-8000.app.github.dev/`
- **Admin Panel:** `https://{your-codespace}-8000.app.github.dev/admin/`

---

## 📋 What's Available to Test

### ✅ Working Now

1. **Home Page** - Clean modern interface with system status
2. **Admin Panel** - Full Django admin for all core_foundation models
3. **Core Foundation Models** (12 models):
   - UserPreference
   - CostCenter
   - Currency & ExchangeRate
   - ERPReference & ERPDocumentType
   - Notification
   - ActivityLog
   - ApprovalType & ApprovalAuthority
   - LossOfSaleCause & LossOfSaleEvent

### ⏳ Coming Soon

- Core Dashboard (depends on HR, Inventory, Production apps)
- Operational modules (to be migrated)

---

## 🧪 Testing Checklist

### Basic Functionality Tests

- [ ] **Home page loads** without errors
- [ ] **Navigation works** (Home, Admin links)
- [ ] **Login/Logout** functions properly
- [ ] **Admin panel** accessible at `/admin/`
- [ ] **Static files** load (CSS, JS, icons)
- [ ] **Database connection** works

### Core Foundation Model Tests

Test each model in admin panel:

- [ ] **CostCenter** - Create, Read, Update, Delete
- [ ] **Currency** - Add currencies, test exchange rates
- [ ] **UserPreference** - User settings and themes
- [ ] **Notification** - Create notifications
- [ ] **ERPReference** - ERP integration mappings
- [ ] **ActivityLog** - View system logs

### Admin Interface Tests

- [ ] **Create new records** in each model
- [ ] **Edit existing records**
- [ ] **Delete records** with confirmation
- [ ] **Search functionality** works
- [ ] **Filters** work properly
- [ ] **Pagination** displays correctly

### UI/UX Tests

- [ ] **Responsive design** - Test on different window sizes
- [ ] **Bootstrap styles** load correctly
- [ ] **Font Awesome icons** display
- [ ] **Alerts/Messages** show and auto-dismiss
- [ ] **Navigation** is intuitive
- [ ] **Footer** shows correct environment info

---

## 🔧 Common Testing Commands

```bash
# Activate virtual environment (if not active)
source venv/bin/activate

# Run system check
python manage.py check

# Check migrations status
python manage.py showmigrations

# Create new migrations (if models changed)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Access Django shell
python manage.py shell

# Create test data
python manage.py shell
>>> from core_foundation.models import CostCenter
>>> CostCenter.objects.create(code='CC001', name='Test Center', is_active=True)

# View database directly
python manage.py dbshell
```

---

## 🐛 Troubleshooting

### Server won't start

```bash
# Check if port 8000 is in use
lsof -ti:8000

# Kill process on port 8000
kill -9 $(lsof -ti:8000)

# Try again
./start.sh
```

### Static files not loading

```bash
# Collect static files
python manage.py collectstatic --noinput

# Restart server
```

### Database connection error

```bash
# Check PostgreSQL status
pg_isready -h db -U postgres

# If not ready, wait a moment and try again
# The setup script waits up to 60 seconds for PostgreSQL
```

### Migration errors

```bash
# Check which migrations are applied
python manage.py showmigrations

# If migrations are unapplied
python manage.py migrate

# If migrations are corrupted, you may need to reset
# (CAUTION: This will delete all data!)
python manage.py migrate core_foundation zero
python manage.py migrate core_foundation
```

### Environment issues

```bash
# Verify .env file exists
cat .env

# If missing, create it
cp .env.example .env

# Update DB_HOST to 'db' for Codespaces
sed -i 's/DB_HOST=localhost/DB_HOST=db/g' .env
```

---

## 📊 Test Data

### Sample Cost Centers

```python
from core_foundation.models import CostCenter

CostCenter.objects.create(
    code='PROD001',
    name='Production Department',
    description='Main production floor',
    is_active=True
)

CostCenter.objects.create(
    code='ADMIN001',
    name='Administration',
    description='Administrative overhead',
    is_active=True
)
```

### Sample Currencies

```python
from core_foundation.models import Currency

Currency.objects.create(
    code='USD',
    name='US Dollar',
    symbol='$',
    is_active=True
)

Currency.objects.create(
    code='EUR',
    name='Euro',
    symbol='€',
    is_active=True
)
```

---

## 🚀 Performance Testing

### Load Testing Basics

```bash
# Install Apache Bench (if not available)
# ab -n 100 -c 10 https://{your-codespace}-8000.app.github.dev/

# Check query performance
python manage.py shell
>>> from django.db import connection
>>> from django.test.utils import override_settings
>>> # Run queries and check connection.queries
```

---

## 📝 Reporting Issues

When reporting issues, include:

1. **What you were testing** (e.g., "Creating new CostCenter")
2. **Steps to reproduce**
3. **Expected behavior**
4. **Actual behavior**
5. **Error messages** (if any)
6. **Screenshots** (if UI issue)
7. **Browser/Environment** (Codespaces, Chrome, etc.)

### Get Debug Info

```bash
# Django version
python manage.py version

# System check with deployment checks
python manage.py check --deploy

# Database info
python manage.py dbshell
\l  -- List databases
\dt  -- List tables
\q  -- Quit
```

---

## ✅ Sign-Off Tests

Before considering a feature "tested", verify:

- [ ] Feature works as expected
- [ ] No console errors in browser
- [ ] No Python errors in terminal
- [ ] Data persists after page reload
- [ ] Works for both superuser and regular users (if applicable)
- [ ] Responsive design looks good
- [ ] Page loads in < 2 seconds

---

## 🎓 Learning Resources

- **Django Docs:** https://docs.djangoproject.com/
- **Bootstrap 5:** https://getbootstrap.com/docs/5.3/
- **PostgreSQL:** https://www.postgresql.org/docs/
- **GitHub Codespaces:** https://docs.github.com/en/codespaces

---

## 📞 Support

If you encounter issues:

1. Check `docs/TROUBLESHOOTING.md`
2. Review `docs/CODESPACES_GUIDE.md`
3. Check server logs in terminal
4. Review browser console for errors

---

**Happy Testing! 🎉**

Last Updated: 2025-11-22
