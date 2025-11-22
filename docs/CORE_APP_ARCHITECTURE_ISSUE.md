# Core App Architecture Issue - Circular Dependencies

**Date:** 2025-11-22
**Severity:** High
**Status:** Documented, Needs Resolution

---

## Issue Summary

The `core` app has extensive dependencies on almost all other apps in the system, making it **NOT a true foundation app**. This creates a circular dependency problem that prevents full activation of core views and URLs until other apps are migrated.

---

## Affected Files

### Files with Cross-App Dependencies:

1. **core/views.py** (line 27+)
   - Imports: HR, Inventory, Production, Evaluation, Purchasing, QRCodes, Knowledge, Maintenance, Quality, Planning, Sales
   - Impact: Cannot load main_dashboard view without these apps

2. **core/services/kpi_service.py**
   - Imports: HR, Inventory, Production, Purchasing, Evaluation, QRCodes
   - Impact: KPI calculations depend on all major apps

3. **core/services/planning_service.py**
   - Imports: Production, Inventory, HR, Purchasing
   - Impact: Planning features depend on operational apps

4. **core/management/commands/load_test_data.py**
   - Imports: HR (Department), Inventory (Location)
   - Impact: Cannot load test data without these models

5. **core/tests/test_global_search.py**
   - Imports: HR, Inventory, Engineering
   - Impact: Tests cannot run until these apps exist

---

## Current Status

### ✅ What Works:

- ✅ Core models (12 models) - **Fully functional**
- ✅ Migrations - **Applied successfully**
- ✅ Admin interface for core models
- ✅ Django check passes (0 errors)
- ✅ Template files present (19 HTML files)
- ✅ Static files present (CSS, JS)
- ✅ Utility modules present (forms, export, search, notifications)

### ❌ What's Disabled:

- ❌ Core URLs - **Commented out** in floor_project/urls.py
- ❌ Dashboard views - Depend on HR, Production, etc.
- ❌ KPI service - Depends on all operational apps
- ❌ Global search - Depends on HR, Inventory, Engineering
- ❌ Planning service - Depends on Production, Inventory, HR

---

## Migration Strategy Impact

### Original Plan Assumption:
**Core → HR → Inventory → Production → ...**
(Core as foundation, then build other apps on top)

### Reality Discovered:
**HR + Inventory + Production + ... → Core**
(Core is actually an aggregator/dashboard, not foundation)

### Architectural Issue:

The old repository has this structure:
```
core/
├── models.py          ← Foundation models (CostCenter, Currency, etc.)
├── views.py           ← Dashboard that aggregates ALL apps
├── services/          ← KPIs and planning that need ALL apps
└── templates/         ← Main dashboard showing ALL apps
```

**Problem:** Models are foundational, but views/services are aggregators.

---

## Resolution Options

### Option 1: Split Core App (Recommended)

**Refactor core into two apps:**

1. **core_foundation** (true foundation)
   - Models: UserPreference, CostCenter, Currency, etc.
   - No dependencies on other apps
   - Migrated first

2. **dashboard** (aggregator)
   - Views: main_dashboard, finance_dashboard
   - Services: KPI calculations, planning
   - Templates: Aggregate views
   - Migrated LAST (after all apps exist)

**Pros:**
- Clean separation of concerns
- Logical dependency tree
- Easy to understand

**Cons:**
- Requires refactoring
- Changes from old repo structure

### Option 2: Keep Core Intact, Migrate Last

**Keep core as-is, but change migration order:**

1. Migrate: HR, Inventory, Production, etc. (without core)
2. Migrate: Core (after all dependencies exist)

**Pros:**
- No refactoring needed
- Matches old repo structure

**Cons:**
- Counter-intuitive (core migrated last)
- No shared models until end
- Other apps can't use CostCenter, Currency early

### Option 3: Conditional Imports in Core

**Use try/except in core views:**

```python
# core/views.py
try:
    from hr.models import HREmployee
except ImportError:
    HREmployee = None

def main_dashboard(request):
    if HREmployee is not None:
        # Show HR section
    else:
        # Skip HR section
```

**Pros:**
- Core can be partially functional
- Graceful degradation

**Cons:**
- Complex conditional logic
- Hard to maintain
- Doesn't solve the architectural issue

---

## Recommended Approach

### Phase 2 Revised Migration Plan:

1. **Extract core foundation models**
   - Create migration for CostCenter, Currency, Notification, ActivityLog
   - Keep models only (no views/services)
   - Name it "core" or "core_foundation"

2. **Migrate operational apps**
   - HR, Inventory, Production, etc.
   - Can now use core foundation models

3. **Migrate core dashboard features**
   - After all apps exist, migrate core views/services/templates
   - Add core URLs
   - Or create separate "dashboard" app

---

## Current Workaround

**Temporary Solution:**

- ✅ All core files migrated (47 files)
- ✅ Models functional and tested
- ❌ URLs commented out in floor_project/urls.py (line 22-23)
- ❌ Views will error if called directly

**To activate core views later:**

1. Wait until HR, Inventory, Production, etc. are migrated
2. Uncomment in floor_project/urls.py:
   ```python
   path('', include('core.urls', namespace='core')),
   ```

3. Test dashboard views

---

## Files Affected

### Imports to Fix Later:

| File | Dependencies | Status |
|------|--------------|--------|
| core/views.py | 11 apps | Needs all apps |
| core/services/kpi_service.py | 6 apps | Needs all apps |
| core/services/planning_service.py | 4 apps | Needs 4 apps |
| core/management/commands/load_test_data.py | 2 apps | Needs HR + Inventory |
| core/tests/test_global_search.py | 3 apps | Needs HR + Inventory + Engineering |

---

## Next Steps

1. **Immediate:**
   - [x] Document this issue (this file)
   - [x] Commit core app with views disabled
   - [x] Push to GitHub

2. **Short-term:**
   - [ ] Decide on Option 1, 2, or 3 above
   - [ ] Update Phase 2 migration plan accordingly
   - [ ] Communicate decision to team

3. **Long-term:**
   - [ ] If Option 1: Refactor core into foundation + dashboard
   - [ ] If Option 2: Change migration order (core last)
   - [ ] If Option 3: Add conditional imports

---

## Technical Debt Note

This dependency structure suggests the old repository may have grown organically without clear architectural boundaries. The "core" app became a catch-all for:
- Foundation models (good ✅)
- Dashboard views (should be separate app ❌)
- Cross-app services (should be separate app ❌)

**Recommendation:** Use Phase 2 migration as opportunity to improve architecture.

---

**Document maintained by:** Floor Management System Migration Team
**Last updated:** 2025-11-22
**Review:** Required before proceeding with HR/Inventory migration
