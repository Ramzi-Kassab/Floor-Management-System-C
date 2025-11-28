# 🚀 Quick Reference Guide

## Files I Created For You

| File | Purpose | How to Use |
|------|---------|------------|
| `PROJECT_CONTEXT.md` | Remember project context in future chats | Copy to your repo, reference in new Claude chats |
| `CLAUDE_CODE_PROMPT_COMPREHENSIVE.md` | Complete prompt for Claude Code | Copy entire content and paste to Claude Code |

---

## 📋 Step-by-Step: What to Do Now

### Step 1: Download These Files

Click the links below to download:
- [PROJECT_CONTEXT.md](computer:///home/claude/outputs/PROJECT_CONTEXT.md)
- [CLAUDE_CODE_PROMPT_COMPREHENSIVE.md](computer:///home/claude/outputs/CLAUDE_CODE_PROMPT_COMPREHENSIVE.md)

### Step 2: Add PROJECT_CONTEXT.md to Your Repo

In your Codespaces terminal:
```bash
# Navigate to your project
cd /workspaces/Floor-Management-System-C

# Create the file (paste the content from PROJECT_CONTEXT.md)
# Or upload it via VS Code

# Commit it
git add PROJECT_CONTEXT.md
git commit -m "docs: add project context for future reference"
git push
```

### Step 3: Send Prompt to Claude Code

1. Open Claude Code (claude.ai/code or your Claude Code session)
2. Copy the ENTIRE content of `CLAUDE_CODE_PROMPT_COMPREHENSIVE.md`
3. Paste it as your message
4. Let Claude Code implement the changes

### Step 4: After Claude Code Finishes

In your Codespaces terminal:
```bash
# Kill any running server
pkill -f "manage.py runserver"

# Pull the changes
git fetch origin
git reset --hard origin/claude/create-production-department-01GGfP6mxzwRoRUKtaE66GbR

# Clear caches
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput --clear

# Start server
python manage.py runserver 0.0.0.0:8000
```

### Step 5: Test the Changes

1. Open **Incognito** window (`Ctrl+Shift+N`)
2. Go to: `https://YOUR-CODESPACE-NAME-8000.app.github.dev/production/designs/hub/`
3. Verify:
   - ✅ Table grid is aligned
   - ✅ Columns button shows column checkboxes
   - ✅ Entry Level column appears
   - ✅ Entry Source badges display

---

## 🔄 Quick Commands Cheatsheet

### Update from GitHub to Codespaces
```bash
git pull && python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000
```

### Full Rebuild
```bash
pkill -f "manage.py runserver"; sleep 2; git fetch origin && git reset --hard origin/claude/create-production-department-01GGfP6mxzwRoRUKtaE66GbR && find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null; pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput --clear && python manage.py runserver 0.0.0.0:8000
```

### Check for Errors
```bash
python manage.py check
```

### Create Superuser
```bash
python manage.py createsuperuser
# Username: admin
# Password: Ra@mzi@123
```

---

## 💡 Starting a New Claude Chat

When you start a new conversation with Claude, paste this:

```
I'm working on the Floor Management System Django project.
GitHub: https://github.com/Ramzi-Kassab/Floor-Management-System-C
Branch: claude/create-production-department-01GGfP6mxzwRoRUKtaE66GbR

Key context:
- Production app with BitDesign and BitDesignRevision models
- Bit Design Hub at /production/designs/hub/
- Levels 1-6 represent manufacturing stages
- Recently added: Flexible Entry Levels (designs can start at any level)

See PROJECT_CONTEXT.md in the repo for full details.

[Then describe your specific task/question]
```

---

## 📊 What the Enhancement Does

### Before (Current):
- All designs MUST start at Level 1
- No tracking of where designs come from
- Hub shows only Level 1 as "Design root"

### After (Enhanced):
- Designs can start at ANY level (1-6)
- Track entry source: In-House, Purchased, Customer, Refurb, JV
- Track supplier for purchased items
- Hub shows entry level with badge
- Filter by entry level and source

### Use Cases Enabled:
1. **Purchased L4 Assembly**: Import a welded head+upper from supplier
2. **Refurb at L5**: Take existing bit with cutters, refurbish it
3. **JV L3 Kit**: Receive kit from joint venture partner
4. **Customer L6**: Customer supplies ready-to-run bit for evaluation

---

## ✅ Success Criteria

After implementation, verify:

1. **Hub Table UI**
   - [ ] No gaps between cells
   - [ ] Headers fully visible
   - [ ] Columns button shows checkboxes
   - [ ] Column hide/show works

2. **Flexible Entry Levels**
   - [ ] Entry column in hub table
   - [ ] Entry source badges display
   - [ ] Create form has entry fields
   - [ ] Filter by entry level works

3. **No Regressions**
   - [ ] Existing designs still work
   - [ ] Clone/branch still works
   - [ ] MAT levels still work
   - [ ] No errors in console
