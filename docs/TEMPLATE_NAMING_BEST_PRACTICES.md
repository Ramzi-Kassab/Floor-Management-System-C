# Template Naming Best Practices - Floor Management System

**Document Version:** 1.0.0
**Last Updated:** 2025-11-22
**Status:** Mandatory - All apps must follow

---

## The Problem: Template Name Collisions

### What Happens Without Namespacing

When multiple Django apps have templates with the same name, Django's template loader will find the **first match** based on `INSTALLED_APPS` order, causing unpredictable behavior.

**Example of the problem:**

```python
# settings.py
INSTALLED_APPS = [
    'core',
    'hr',
    'inventory',
]
```

```
Project Structure:
core/templates/dashboard.html           ← Django finds this first
hr/templates/dashboard.html             ← This is ignored!
inventory/templates/dashboard.html      ← This is also ignored!
```

```python
# hr/views.py
def hr_dashboard(request):
    return render(request, 'dashboard.html')  # ❌ Loads core/dashboard.html!
```

**Result:** HR dashboard view shows the CORE dashboard template instead! 🐛

---

## ✅ The Solution: Always Namespace Templates

### Django Best Practice

**Create a subdirectory matching your app name inside templates/:**

```
✅ CORRECT Structure:
core/templates/core/dashboard.html          ← Namespaced
hr/templates/hr/dashboard.html              ← Namespaced
inventory/templates/inventory/dashboard.html ← Namespaced
```

```python
# hr/views.py
def hr_dashboard(request):
    return render(request, 'hr/dashboard.html')  # ✅ Explicit, no conflict
```

---

## Mandatory Template Structure

### For Every Django App:

```
<app_name>/
├── templates/
│   └── <app_name>/              ← Must match app name!
│       ├── base.html            ← App-specific base (if needed)
│       ├── dashboard.html       ← Main app view
│       ├── <model>_list.html    ← List views
│       ├── <model>_detail.html  ← Detail views
│       ├── <model>_form.html    ← Create/Edit forms
│       └── partials/            ← Reusable components
│           ├── _table.html
│           └── _filters.html
└── ...
```

### Example: HR App

```
hr/
├── templates/
│   └── hr/                      ← Namespace: matches app name
│       ├── dashboard.html       ← hr/dashboard.html
│       ├── employee_list.html   ← hr/employee_list.html
│       ├── employee_detail.html ← hr/employee_detail.html
│       ├── employee_form.html   ← hr/employee_form.html
│       ├── department_list.html
│       └── partials/
│           ├── _employee_card.html
│           └── _department_tree.html
└── ...
```

**In views:**
```python
# hr/views.py
from django.shortcuts import render

def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'hr/employee_list.html', {  # ✅ Explicit
        'employees': employees
    })

def hr_dashboard(request):
    return render(request, 'hr/dashboard.html')  # ✅ No conflict with core/dashboard.html
```

---

## Common Template Names - Use Case Specific Naming

### Avoid Generic Names Without Namespace

| ❌ Bad (Collision-prone) | ✅ Good (Namespaced) |
|-------------------------|---------------------|
| `dashboard.html` | `core/main_dashboard.html` |
| `list.html` | `hr/employee_list.html` |
| `detail.html` | `inventory/item_detail.html` |
| `form.html` | `production/jobcard_form.html` |
| `create.html` | `purchasing/supplier_create.html` |

### Recommended Template Naming Convention

**Format:** `<app>/<model>_<action>.html`

**Examples:**
- `hr/employee_list.html` - List of employees
- `hr/employee_detail.html` - Single employee detail
- `hr/employee_form.html` - Create/edit employee (handles both)
- `hr/employee_create.html` - Create only (if different from edit)
- `hr/employee_update.html` - Update only (if different from create)
- `hr/employee_delete.html` - Delete confirmation

**Dashboard templates:**
- `core/main_dashboard.html` - System-wide main dashboard
- `hr/hr_dashboard.html` - HR department dashboard
- `inventory/inventory_dashboard.html` - Inventory dashboard
- `production/production_dashboard.html` - Production dashboard

---

## Partials and Reusable Components

### Partials Should Also Be Namespaced

```
✅ CORRECT:
core/templates/core/partials/_data_table.html
hr/templates/hr/partials/_employee_card.html
inventory/templates/inventory/partials/_stock_level.html
```

**Naming convention for partials:**
- Prefix with underscore: `_partial_name.html`
- Place in `<app>/templates/<app>/partials/` directory
- Use descriptive names: `_employee_card.html` not `_card.html`

**Usage in templates:**
```django
{# In hr/employee_list.html #}
{% for employee in employees %}
    {% include 'hr/partials/_employee_card.html' with employee=employee %}
{% endfor %}
```

---

## Base Templates

### Project-Level Base

```
templates/
└── base.html           ← Project-wide base template
```

**Used by:** All apps extend this for common layout (navbar, footer, etc.)

```django
{# templates/base.html #}
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Floor Management System{% endblock %}</title>
</head>
<body>
    {% include 'partials/_navbar.html' %}

    <main>
        {% block content %}{% endblock %}
    </main>

    {% include 'partials/_footer.html' %}
</body>
</html>
```

### App-Level Base (Optional)

```
core/templates/core/base.html      ← Core-specific base (extends project base)
hr/templates/hr/base.html          ← HR-specific base (extends project base)
```

**Example:**
```django
{# hr/templates/hr/base.html #}
{% extends 'base.html' %}

{% block content %}
    <div class="hr-layout">
        <aside class="hr-sidebar">
            {% include 'hr/partials/_hr_menu.html' %}
        </aside>

        <div class="hr-content">
            {% block hr_content %}{% endblock %}
        </div>
    </div>
{% endblock %}
```

```django
{# hr/templates/hr/employee_list.html #}
{% extends 'hr/base.html' %}

{% block hr_content %}
    <h1>Employees</h1>
    {# ... employee list ... #}
{% endblock %}
```

---

## Template Inheritance Hierarchy

```
templates/base.html (project-wide)
    ↓
core/templates/core/base.html (core-specific)
    ↓
core/templates/core/main_dashboard.html

templates/base.html (project-wide)
    ↓
hr/templates/hr/base.html (hr-specific)
    ↓
hr/templates/hr/employee_list.html
```

---

## Migration Checklist

When migrating templates from old repo:

- [ ] Check template is in app-specific directory: `<app>/templates/<app>/`
- [ ] Update any `{% include %}` tags to use namespaced paths
- [ ] Update any `{% extends %}` tags to use namespaced paths
- [ ] Update view `render()` calls to use namespaced paths
- [ ] Check for duplicate template names across apps
- [ ] Rename generic templates to be more specific (e.g., `list.html` → `employee_list.html`)
- [ ] Move partials to `<app>/templates/<app>/partials/`
- [ ] Prefix partial names with underscore
- [ ] Test that templates load correctly
- [ ] Verify no template conflicts with other apps

---

## Current Project Status

### ✅ Apps Following Best Practices:

**core_foundation:**
- No templates (models only) ✅

**core (dashboard):**
- ✅ `core/templates/core/main_dashboard.html`
- ✅ `core/templates/core/finance_dashboard.html`
- ✅ `core/templates/core/user_preferences.html`
- ✅ `core/templates/core/costcenter_list.html`
- ✅ `core/templates/core/partials/_data_table.html`
- ✅ All 19 templates properly namespaced

**Future apps:**
- HR templates must go in: `hr/templates/hr/`
- Inventory templates must go in: `inventory/templates/inventory/`
- Production templates must go in: `production/templates/production/`

---

## Template Loader Configuration

**Verify in settings.py:**

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Project-wide templates
        'APP_DIRS': True,  # ← Must be True for app templates
        'OPTIONS': {
            'context_processors': [
                # ...
            ],
        },
    },
]
```

**How Django finds templates with `APP_DIRS=True`:**

1. Check project-wide `templates/` directory
2. Check each app in `INSTALLED_APPS` order: `<app>/templates/`
3. Return first match

**This is why namespacing is critical!**

---

## Anti-Patterns to Avoid

### ❌ Don't Do This:

```
# ❌ Templates not namespaced
core/templates/dashboard.html
core/templates/list.html
core/templates/form.html

# ❌ Generic names
hr/templates/index.html
hr/templates/view.html

# ❌ Mixing apps in same directory
templates/
├── core_dashboard.html
├── hr_dashboard.html
└── inventory_dashboard.html
```

### ✅ Do This Instead:

```
# ✅ Properly namespaced
core/templates/core/main_dashboard.html
core/templates/core/costcenter_list.html
core/templates/core/costcenter_form.html

# ✅ Descriptive names
hr/templates/hr/hr_dashboard.html
hr/templates/hr/employee_list.html

# ✅ App-specific directories
core/templates/core/
hr/templates/hr/
inventory/templates/inventory/
```

---

## Testing Template Namespacing

### Check for Template Conflicts:

```bash
# Find all templates named "dashboard.html"
find . -path "*/templates/*" -name "dashboard.html"

# Expected output (all namespaced):
./core/templates/core/main_dashboard.html
./hr/templates/hr/hr_dashboard.html

# Bad output (conflicts possible):
./core/templates/dashboard.html
./hr/templates/dashboard.html
```

### Test Template Loading in Shell:

```python
python manage.py shell

>>> from django.template.loader import get_template
>>>
>>> # This should work:
>>> template = get_template('hr/employee_list.html')
>>> print(template.origin.name)
# Should show: /path/to/hr/templates/hr/employee_list.html
>>>
>>> # This would be ambiguous without namespacing:
>>> template = get_template('dashboard.html')  # Which dashboard?
```

---

## Summary

### The Golden Rules:

1. **Always namespace templates** - Create `<app>/templates/<app>/` directory
2. **Use descriptive names** - `employee_list.html` not `list.html`
3. **Prefix partials with underscore** - `_employee_card.html`
4. **Keep partials in partials/ subdirectory** - `<app>/templates/<app>/partials/`
5. **Test for conflicts** - Search for duplicate template names
6. **Update all references** - Views, includes, extends must use namespaced paths

### Quick Reference:

| Template Type | Path Format | Example |
|--------------|-------------|---------|
| List view | `<app>/templates/<app>/<model>_list.html` | `hr/templates/hr/employee_list.html` |
| Detail view | `<app>/templates/<app>/<model>_detail.html` | `hr/templates/hr/employee_detail.html` |
| Form | `<app>/templates/<app>/<model>_form.html` | `hr/templates/hr/employee_form.html` |
| Dashboard | `<app>/templates/<app>/<app>_dashboard.html` | `hr/templates/hr/hr_dashboard.html` |
| Partial | `<app>/templates/<app>/partials/_<name>.html` | `hr/templates/hr/partials/_employee_card.html` |
| Base | `<app>/templates/<app>/base.html` | `hr/templates/hr/base.html` |

---

**Document maintained by:** Floor Management System Development Team
**Mandatory compliance:** All new and migrated templates
**Violations:** Will be rejected in code review
