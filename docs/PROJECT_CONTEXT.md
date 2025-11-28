# Floor Management System - Project Context

**Use this document when starting new Claude chats to provide context.**

---

## 🎯 Quick Start for New Chats

Copy and paste this at the beginning of any new Claude conversation:

```
I'm working on the Floor Management System Django project for a drilling bits factory.

GitHub: https://github.com/Ramzi-Kassab/Floor-Management-System-C
Branch: claude/create-production-department-01GGfP6mxzwRoRUKtaE66GbR

Key context:
- Django 5.2.6 with Bootstrap 5 frontend
- Production app tracks bit designs through manufacturing levels (1-6)
- BitDesign model = master design specs
- BitDesignRevision model = MAT numbers at different manufacturing levels
- Bit Design Hub page at /production/designs/hub/ - professional interactive table

Current goals:
1. Fix UI bugs in the Hub table (alignment, column visibility)
2. Allow designs to start at any level (not just Level 1)

See PROJECT_CONTEXT.md in the repo for full details.
```

---

## 📋 Project Overview

### What is this system?

A **Floor Management System** for a drilling bits factory that manufactures:
- **PDC (Fixed Cutter) bits**: Matrix-body and Steel-body
- **Roller Cone bits**

The system tracks:
- Bit designs and specifications
- Manufacturing workflows (New Build, Repair)
- Work orders and job cards
- Quality control and evaluation
- Infiltration department (Matrix body production)

### Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Django 5.2.6 |
| Database | PostgreSQL (production) / SQLite (Codespaces dev) |
| Frontend | Bootstrap 5, vanilla JavaScript |
| Auth | Django built-in |
| API | Django REST Framework |

---

## 🏗️ Key Models

### BitDesign (production/models.py)

The **master design blueprint** for a bit. Contains all engineering specifications:

```python
class BitDesign(models.Model):
    bit_type          # PDC/RC (Fixed Cutter or Roller Cone)
    size_inch         # Bit diameter (e.g., 8.5, 12.25)
    current_smi_name  # ARDT/SMI type (e.g., HD75WF, MMD53DH-2)
    hdbs_name         # Halliburton design name
    iadc_code         # IADC bit code (e.g., S334, M223)
    body_material     # MATRIX or STEEL
    blade_count       # Number of blades
    cutter_size_category  # Cutter size (3-8)
    gauge_length_inch     # Gauge length
    nozzle_count      # Number of nozzles
    port_count        # Number of ports
    connection_type   # REGULAR, CEREBRO, etc.
    connection_size   # API connection (e.g., 4 1/2 REG)
    connection_end_type  # PIN or BOX
    # ... many more fields
```

### BitDesignRevision (production/models.py)

**MAT numbers at different manufacturing levels**. Each revision represents a physical state:

```python
class BitDesignRevision(models.Model):
    design        # ForeignKey to BitDesign
    mat_number    # Unique material number
    level         # Physical level (2-6)
    previous_level  # ForeignKey to self (level hierarchy)
    effective_from  # When this revision becomes active
    effective_to    # When it expires (null = current)
    upper_welded    # For Level 5: is upper section welded?
    variant_label   # Short label for variant
    variant_notes   # What distinguishes this variant
```

---

## 📊 Level System

Levels represent the **physical manufacturing stages** of a bit:

| Level | Name | Description |
|-------|------|-------------|
| **L1** | Design Root | Master design specifications only |
| **L2** | Molds + Tooling | Mold parts, patterns, displacement inserts, tooling |
| **L3** | Head + Upper Kit | Finished head + matching upper (unwelded, no cutters) |
| **L4** | Welded Assembly | Head + upper welded together, no cutters |
| **L5** | With Cutters | All PDC cutters brazed, may have loose or welded upper |
| **L6** | Ready-to-Run | Field-ready: paint, nozzles, packaging complete |

### Current Limitation

Currently, all designs **must start at Level 1**. The enhancement goal is to allow designs to start at **any level** to support:
- Purchased semi-finished products (start at L3, L4, or L5)
- Refurbishment (start at L5)
- Customer-supplied components
- Outsourced partial manufacturing

---

## 📁 Key Files

### Models
- `production/models.py` - BitDesign, BitDesignRevision, WorkOrder, JobCard, etc.

### Views
- `production/views.py` - BitDesignHubView (line 458), list/detail views

### Templates
- `production/templates/production/bitdesign_hub.html` - Main hub table
- `production/templates/production/base.html` - Base template
- `production/templates/production/bitdesign_detail.html` - Design detail page
- `production/templates/production/bitdesign_form.html` - Create/edit form

### Static Files
- `production/static/production/css/bitdesign-hub-table.css` - Hub table styles
- `production/static/production/js/bitdesign-hub-table.js` - Hub table interactivity

### URLs
- `production/urls.py` - All production app routes

---

## 🔗 Key URLs

| URL | View | Purpose |
|-----|------|---------|
| `/production/` | ProductionDashboardView | Dashboard |
| `/production/designs/` | BitDesignListView | List all designs |
| `/production/designs/hub/` | BitDesignHubView | **Main Hub** with collapsible levels |
| `/production/designs/<pk>/` | BitDesignDetailView | Design detail |
| `/production/designs/create/` | BitDesignCreateView | Create new design |
| `/production/designs/<pk>/edit/` | BitDesignUpdateView | Edit design |
| `/production/designs/<pk>/mat-levels/` | BitMatLevelListView | MAT levels for design |

---

## 🖥️ Codespaces Setup

### Quick Start Command
```bash
# Update and run
git pull && python manage.py migrate && python manage.py runserver 0.0.0.0:8000
```

### Full Rebuild Command
```bash
pkill -f "manage.py runserver"; sleep 2; git fetch origin && git reset --hard origin/claude/create-production-department-01GGfP6mxzwRoRUKtaE66GbR && find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null; pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput --clear && python manage.py runserver 0.0.0.0:8000
```

### Important Notes
- Use **SQLite** for development (PostgreSQL has sudo issues in Codespaces)
- Set UTF-8 environment for Arabic text support
- Access app via **PORTS tab** in Codespaces, not localhost
- Always **hard refresh** (`Ctrl+Shift+R`) or use **Incognito** to see changes

### Admin Credentials
- Username: `admin`
- Password: `Ra@mzi@123`

---

## 🐛 Known Issues & Fixes

### 1. CSRF Error
**Solution**: Add localhost to CSRF_TRUSTED_ORIGINS in settings.py

### 2. Unicode/Arabic Errors
**Solution**: Set UTF-8 environment variables, disable i18n temporarily

### 3. PostgreSQL Connection Refused
**Solution**: Use SQLite instead for Codespaces

### 4. Static Files Not Updating
**Solution**: Run `python manage.py collectstatic --noinput --clear`

### 5. Browser Cache
**Solution**: Hard refresh (Ctrl+Shift+R) or Incognito mode

---

## 🎯 Current Enhancement Goals

### Goal 1: Fix Hub Table UI Bugs
- [ ] Fix grid alignment (no gaps between cells)
- [ ] Fix header content visibility (no clipping)
- [ ] Fix Columns button (show column visibility, not filter conditions)
- [ ] Make filters functional

### Goal 2: Flexible Entry Levels
Allow designs to start at any level (L1-L6):
- Add `entry_level` field to BitDesign
- Add `entry_source` field (In-House, Purchased, Refurb, Customer)
- Add `entry_supplier` field for purchased items
- Update Hub view to show entry point
- Update forms to allow entry level selection

---

## 📝 Commit Message Convention

```
type(scope): description

Types: feat, fix, docs, style, refactor, test, chore
Scope: production, core, hub, models, views, etc.

Examples:
feat(production): Add flexible entry level to BitDesign
fix(hub): Fix table grid alignment
docs: Update PROJECT_CONTEXT.md
```

---

## 🔄 Git Workflow

1. **Pull latest changes**: `git pull`
2. **Make changes**
3. **Test**: `python manage.py check`
4. **Commit**: `git add . && git commit -m "type(scope): description"`
5. **Push**: `git push`
6. **In Codespaces**: Run rebuild command and test

---

## 📞 Contact

Repository Owner: Ramzi-Kassab
GitHub: https://github.com/Ramzi-Kassab/Floor-Management-System-C
