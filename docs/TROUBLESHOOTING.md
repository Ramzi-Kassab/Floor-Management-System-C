# Troubleshooting Guide - Codespaces

## Quick Fixes for Common Issues

### ✅ Everything Working?
Run this to verify:
```bash
source venv/bin/activate
python manage.py check
```

Should see: `System check identified no issues (0 silenced).`

---

## Issue 1: Setup Script Failed

**Symptoms:**
- No `venv/` folder
- Dependencies not installed
- Migrations didn't run

**Solution:**
```bash
# Run setup script manually
bash .devcontainer/setup.sh

# Or step-by-step:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

---

## Issue 2: PostgreSQL Not Ready

**Symptoms:**
- `psycopg2.OperationalError: could not connect`
- `connection refused`

**Solution:**
```bash
# Check if PostgreSQL is running
pg_isready -h db -U postgres

# Wait for it
until PGPASSWORD=postgres psql -h db -U postgres -c '\q' 2>/dev/null; do
  echo "Waiting..."
  sleep 2
done

# Then run migrations
python manage.py migrate
```

---

## Issue 3: Virtual Environment Not Activated

**Symptoms:**
- `python: command not found`
- Wrong Python version
- `pip: command not found`

**Solution:**
```bash
source venv/bin/activate

# Verify
which python  # Should show /workspace/venv/bin/python
```

**Make it automatic:**
Add to `~/.bashrc`:
```bash
echo "source /workspace/venv/bin/activate" >> ~/.bashrc
```

---

## Issue 4: Port 8000 Already in Use

**Symptoms:**
- `Error: That port is already in use`

**Solution:**
```bash
# Option 1: Kill existing process
pkill -f runserver

# Option 2: Use different port
python manage.py runserver 0.0.0.0:8001
```

---

## Issue 5: .env File Missing

**Symptoms:**
- `KeyError: 'SECRET_KEY'`
- Database connection errors

**Solution:**
```bash
# Copy from example
cp .env.example .env

# For Codespaces, edit DB_HOST
sed -i 's/DB_HOST=localhost/DB_HOST=db/' .env
```

---

## Issue 6: Migrations Not Applied

**Symptoms:**
- `no such table: django_session`
- Database errors when running server

**Solution:**
```bash
# Check migration status
python manage.py showmigrations

# Apply all migrations
python manage.py migrate

# If stuck, try:
python manage.py migrate --run-syncdb
```

---

## Issue 7: Can't Access Django Admin

**Symptoms:**
- Port forwarding not working
- Can't open localhost:8000

**Solution:**
```bash
# Use 0.0.0.0 to bind all interfaces
python manage.py runserver 0.0.0.0:8000

# Codespaces will show popup to open forwarded port
```

---

## Issue 8: Permission Denied

**Symptoms:**
- `Permission denied` when writing files

**Solution:**
```bash
# Fix ownership
sudo chown -R vscode:vscode /workspace

# Or for specific directories
sudo chown -R vscode:vscode media/ staticfiles/
```

---

## Issue 9: Database Already Exists Error

**Symptoms:**
- `database "floor_management_c" already exists`

**Solution:**
```bash
# This is actually fine! Database persists in Codespace
# Just run migrations
python manage.py migrate
```

---

## Issue 10: GitHub Authentication Failed

**Symptoms:**
- Can't push to GitHub
- `Authentication failed`

**Solution:**
```bash
# Codespaces should auto-authenticate
# But if needed, set up git:
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"

# Use GitHub CLI
gh auth login
```

---

## Complete Reset (Nuclear Option)

If everything is broken:

### Option 1: Delete and Recreate Codespace
1. Stop Codespace
2. Delete Codespace
3. Create new one (your code is safe in GitHub)

### Option 2: Reset PostgreSQL
```bash
# Stop Django server first (Ctrl+C)

# Drop and recreate database
PGPASSWORD=postgres psql -h db -U postgres -c "DROP DATABASE floor_management_c;"
PGPASSWORD=postgres psql -h db -U postgres -c "CREATE DATABASE floor_management_c;"

# Run migrations
python manage.py migrate
```

### Option 3: Fresh Setup
```bash
# Remove venv
rm -rf venv

# Run setup again
bash .devcontainer/setup.sh
```

---

## Diagnostic Commands

Run these to gather info:

```bash
# System info
echo "Python: $(python --version)"
echo "Pip: $(pip --version)"
echo "Virtual env: $VIRTUAL_ENV"

# PostgreSQL status
pg_isready -h db -U postgres

# Django status
python manage.py check
python manage.py showmigrations

# Database connection test
python manage.py dbshell -c "SELECT version();"

# Disk space
df -h

# Running processes
ps aux | grep python
```

---

## Still Stuck?

1. Check Codespace logs (Terminal → View logs)
2. Review `.devcontainer/setup.sh` output
3. Try recreating Codespace
4. Check GitHub Codespaces status page

---

## Prevention Tips

✅ **Always activate venv:**
```bash
source venv/bin/activate
```

✅ **Wait for PostgreSQL before migrations**

✅ **Use `python manage.py check` regularly**

✅ **Commit and push changes frequently**

✅ **Stop server with Ctrl+C** (not closing terminal)

---

## Manual Setup Checklist

If auto-setup fails, run these in order:

- [ ] `python -m venv venv`
- [ ] `source venv/bin/activate`
- [ ] `pip install --upgrade pip`
- [ ] `pip install -r requirements.txt`
- [ ] `cp .env.example .env`
- [ ] Edit `.env` (set `DB_HOST=db`)
- [ ] Wait for PostgreSQL (use `pg_isready -h db -U postgres`)
- [ ] `python manage.py migrate`
- [ ] `python manage.py createsuperuser`
- [ ] `python manage.py runserver`

---

**Most issues resolve with:** Re-run setup script or recreate Codespace!
