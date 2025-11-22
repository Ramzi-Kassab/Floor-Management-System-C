# 🚀 Quick Codespaces Start Guide

## ⚡ Get Started in 3 Steps

### Step 1: Create Codespace
1. Go to: https://github.com/Ramzi-Kassab/Floor-Management-System-C
2. Click: **Code** → **Codespaces** → **Create codespace on claude/setup-codespaces-testing-...**
3. Wait 2-3 minutes ☕ (setup runs automatically)

### Step 2: Create Admin User
```bash
# In the Codespace terminal:
source venv/bin/activate
python manage.py createsuperuser
```

### Step 3: Start Server
```bash
./start.sh
```

**🎉 Done!** Click the popup to open in browser.

---

## 📱 What You'll See

### Home Page (`/`)
- System status dashboard
- Migration progress
- Quick action links
- Clean Bootstrap 5 interface

### Admin Panel (`/admin/`)
- Full Django admin
- 12 Core Foundation models ready to test:
  - UserPreference
  - CostCenter
  - Currency & ExchangeRate
  - ERPReference & ERPDocumentType
  - Notification & ActivityLog
  - ApprovalType & ApprovalAuthority
  - LossOfSaleCause & LossOfSaleEvent

---

## 🧪 Quick Tests

### Test 1: Home Page
- [ ] Home page loads without errors
- [ ] Navigation works
- [ ] Shows "GitHub Codespaces" in environment

### Test 2: Admin Panel
```bash
# Navigate to /admin/
# Login with your superuser credentials
```
- [ ] Admin login works
- [ ] Can see Core Foundation models
- [ ] Can create a new CostCenter

### Test 3: Create Sample Data
```python
# In Django shell
python manage.py shell

from core_foundation.models import CostCenter, Currency

# Create cost center
cc = CostCenter.objects.create(
    code='TEST001',
    name='Test Department',
    is_active=True
)
print(f"Created: {cc}")

# Create currency
usd = Currency.objects.create(
    code='USD',
    name='US Dollar',
    symbol='$',
    is_active=True
)
print(f"Created: {usd}")
```

### Test 4: Verify in Admin
- [ ] Go to Admin → Cost Centers
- [ ] See TEST001 in the list
- [ ] Edit and save changes
- [ ] Delete and confirm

---

## 🆘 Troubleshooting

### Server won't start?
```bash
# Kill any existing process
pkill -f runserver

# Try again
./start.sh
```

### Port forwarding not working?
1. Check VS Code ports tab
2. Ensure port 8000 is "Public"
3. Click the globe icon to open

### Database error?
```bash
# Check PostgreSQL
pg_isready -h db -U postgres

# Re-run migrations
python manage.py migrate
```

---

## 📋 Useful Commands

```bash
# Check system status
python manage.py check

# View migrations
python manage.py showmigrations

# Database shell
python manage.py dbshell

# Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic

# Create cache table
python manage.py createcachetable
```

---

## 📚 Full Documentation

- **Complete Testing Guide:** `CODESPACES_TESTING.md`
- **Codespaces Setup:** `docs/CODESPACES_GUIDE.md`
- **Troubleshooting:** `docs/TROUBLESHOOTING.md`
- **Project README:** `README.md`

---

## ✅ Success Checklist

You'll know everything is working when:

- [x] Codespace created and setup completed
- [x] Superuser created
- [x] Server started with `./start.sh`
- [x] Home page loads in browser
- [x] Admin panel accessible
- [x] Can create/edit/delete data
- [x] No errors in browser console
- [x] No errors in terminal

---

## 🎯 What's Next?

After confirming everything works:

1. **Test all Core Foundation models** in admin
2. **Create sample data** for testing
3. **Explore the UI** and navigation
4. **Report any issues** you find
5. **Ready for next app migration!**

---

**Need Help?** Check `CODESPACES_TESTING.md` for detailed troubleshooting.

**Happy Testing! 🎉**
