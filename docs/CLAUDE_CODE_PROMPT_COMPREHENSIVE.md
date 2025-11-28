# COMPREHENSIVE ENHANCEMENT: Bit Design Hub UI Fixes + Flexible Entry Levels

## ⚠️ CRITICAL INSTRUCTIONS - READ FIRST

This is a MAJOR enhancement task with TWO parts:
1. **Part A**: Fix existing UI bugs in the Bit Design Hub table
2. **Part B**: Add Flexible Entry Level system

You MUST complete BOTH parts. Do NOT do minimal changes. Do NOT skip any items.
After each part, verify your changes work before proceeding.

---

# PART A: FIX UI BUGS IN BIT DESIGN HUB

## Files to Modify
- `production/templates/production/bitdesign_hub.html`
- `production/static/production/css/bitdesign-hub-table.css`
- `production/static/production/js/bitdesign-hub-table.js`

---

## Bug 1: Table Grid Alignment Issues

**Problem**: 
- White spaces/gaps between header cells
- Vertical grid lines don't align between header and data rows
- Cell borders are inconsistent

**Required Fix**:
```css
/* Ensure these are set correctly */
#bitdesign-hub-table {
    border-collapse: collapse;
    width: 100%;
}

#bitdesign-hub-table th,
#bitdesign-hub-table td {
    border: 1px solid #dee2e6;
    padding: 8px 12px;
    margin: 0;
}

/* Remove any gap-causing styles */
#bitdesign-hub-table thead tr {
    border-spacing: 0;
}
```

**Verification**: All vertical lines should be continuous from header to last row.

---

## Bug 2: Header Content Cut Off

**Problem**: Filter icons and sort arrows are partially hidden or clipped.

**Required Fix**:
```css
#bitdesign-hub-table thead th {
    min-width: 80px;
    overflow: visible;
    position: sticky;
    top: 0;
    z-index: 10;
    white-space: nowrap;
}

/* Ensure dropdowns are not clipped */
.filter-dropdown,
.column-visibility-menu {
    z-index: 1050;
    position: absolute;
}
```

**Verification**: All header text, icons, and dropdowns fully visible.

---

## Bug 3: "Columns" Button Shows Wrong Content

**Problem**: The Columns dropdown shows filter conditions (Greater Than, Less Than, etc.) instead of column visibility checkboxes.

**Current (WRONG)**:
```
Columns dropdown shows:
- Level Condition
- Contains Equals
- Starts With Ends
- Greater Than Less
- ...
```

**Required (CORRECT)**:
```
┌─────────────────────────────────┐
│ 👁 Show/Hide Columns           │
├─────────────────────────────────┤
│ ☑ Level                        │
│ ☑ MAT                          │
│ ☑ Type                         │
│ ☑ Size                         │
│ ☑ SMI Name                     │
│ ☑ HDBS                         │
│ ☑ IADC                         │
│ ☑ Body                         │
│ ☑ Blades                       │
│ ☑ Cutter Cat                   │
│ ☑ Gauge L.                     │
│ ☑ Conn. Size                   │
│ ☑ Conn. End                    │
│ ☑ Drift                        │
│ ☑ Nozzles                      │
│ ☑ Ports                        │
│ ☑ Nozzle Size                  │
│ ☑ Conn. Type                   │
│ ☑ Breaker W.                   │
│ ☑ Breaker H.                   │
│ ☑ Shank Dia.                   │
│ ☑ Gauge Relief                 │
│ ☑ Active                       │
│ ☑ Actions                      │
├─────────────────────────────────┤
│ [Show All]     [Hide All]      │
└─────────────────────────────────┘
```

**Required JavaScript Fix**:

In `bitdesign-hub-table.js`, find the Columns button initialization and ensure it creates checkboxes for each column, NOT filter conditions:

```javascript
function initColumnVisibility() {
    const table = document.getElementById('bitdesign-hub-table');
    const headers = table.querySelectorAll('thead th');
    const columnsBtn = document.querySelector('.columns-btn') || createColumnsButton();
    const menu = document.querySelector('.column-visibility-menu') || createColumnVisibilityMenu();
    
    // Clear existing content
    menu.innerHTML = '';
    
    // Add title
    const title = document.createElement('div');
    title.className = 'column-visibility-title';
    title.innerHTML = '👁 Show/Hide Columns';
    menu.appendChild(title);
    
    // Add checkbox for each column
    headers.forEach((header, index) => {
        const headerText = header.textContent.trim();
        if (!headerText) return; // Skip empty headers
        
        const item = document.createElement('div');
        item.className = 'column-visibility-item';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `col-vis-${index}`;
        checkbox.checked = true;
        checkbox.dataset.columnIndex = index;
        
        const label = document.createElement('label');
        label.htmlFor = `col-vis-${index}`;
        label.textContent = headerText;
        
        item.appendChild(checkbox);
        item.appendChild(label);
        menu.appendChild(item);
        
        // Toggle column visibility on change
        checkbox.addEventListener('change', function() {
            toggleColumnVisibility(index, this.checked);
        });
    });
    
    // Add Show All / Hide All buttons
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'column-visibility-buttons';
    
    const showAllBtn = document.createElement('button');
    showAllBtn.className = 'btn btn-primary btn-sm';
    showAllBtn.textContent = 'Show All';
    showAllBtn.addEventListener('click', () => {
        menu.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.checked = true;
            toggleColumnVisibility(cb.dataset.columnIndex, true);
        });
    });
    
    const hideAllBtn = document.createElement('button');
    hideAllBtn.className = 'btn btn-secondary btn-sm';
    hideAllBtn.textContent = 'Hide All';
    hideAllBtn.addEventListener('click', () => {
        menu.querySelectorAll('input[type="checkbox"]').forEach((cb, idx) => {
            // Keep first 3 columns always visible (toggle, level, MAT)
            if (idx < 3) return;
            cb.checked = false;
            toggleColumnVisibility(cb.dataset.columnIndex, false);
        });
    });
    
    buttonContainer.appendChild(showAllBtn);
    buttonContainer.appendChild(hideAllBtn);
    menu.appendChild(buttonContainer);
}

function toggleColumnVisibility(columnIndex, visible) {
    const table = document.getElementById('bitdesign-hub-table');
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('th, td');
        if (cells[columnIndex]) {
            cells[columnIndex].style.display = visible ? '' : 'none';
        }
    });
}
```

**Verification**: Clicking Columns button shows a list of column names with checkboxes.

---

## Bug 4: Non-Functional Filters

**Problem**: Filter conditions are listed but don't actually filter data.

**Required Fix**: Either:
A) Make all filters functional, OR
B) Remove non-functional options and keep only working ones

At minimum, these MUST work:
- Text columns: Contains, Equals
- Number columns: Equals, Greater Than, Less Than

**Verification**: Applying a filter actually filters the visible rows.

---

# PART B: FLEXIBLE ENTRY LEVEL SYSTEM

## Overview

Allow BitDesigns to START at any level (2-6), not just Level 1. This supports:
- Purchased semi-finished products
- Refurbishment of existing bits
- Customer-supplied components
- Outsourced partial manufacturing

---

## Step 1: Update BitDesign Model

**File**: `production/models.py`

Add these fields to the `BitDesign` class (after line ~500, in the model fields section):

```python
# ===== FLEXIBLE ENTRY LEVEL FIELDS =====
    
# Entry Level - which level this design enters our system at
ENTRY_LEVEL_CHOICES = [
    (1, 'L1 - Full Design (design specs only)'),
    (2, 'L2 - Tooling (molds, inserts, patterns)'),
    (3, 'L3 - Head + Upper Kit (unwelded, no cutters)'),
    (4, 'L4 - Welded Assembly (no cutters)'),
    (5, 'L5 - With Cutters (brazed, may need finishing)'),
    (6, 'L6 - Ready-to-Run (field-ready bit)'),
]

entry_level = models.PositiveSmallIntegerField(
    choices=ENTRY_LEVEL_CHOICES,
    default=1,
    help_text="The level at which this design enters our manufacturing system"
)

ENTRY_SOURCE_CHOICES = [
    ('INHOUSE', 'In-House Manufacturing'),
    ('PURCHASED', 'Purchased/Acquired'),
    ('CUSTOMER', 'Customer Supplied'),
    ('REFURB', 'Refurbishment'),
    ('JV', 'Joint Venture'),
]

entry_source = models.CharField(
    max_length=20,
    choices=ENTRY_SOURCE_CHOICES,
    default='INHOUSE',
    help_text="How this design enters our system"
)

entry_supplier = models.CharField(
    max_length=100,
    blank=True,
    null=True,
    help_text="Supplier name if entry_source is PURCHASED or JV"
)

entry_notes = models.TextField(
    blank=True,
    help_text="Notes about the entry point (e.g., why starting at this level, supplier details)"
)
```

---

## Step 2: Create Migration

After modifying the model, create a migration:

```bash
python manage.py makemigrations production --name add_flexible_entry_level
```

The migration should:
1. Add `entry_level` field with default=1
2. Add `entry_source` field with default='INHOUSE'
3. Add `entry_supplier` field (nullable)
4. Add `entry_notes` field (blank)

---

## Step 3: Update BitDesign Admin

**File**: `production/admin.py`

Add the new fields to BitDesignAdmin:

```python
@admin.register(BitDesign)
class BitDesignAdmin(admin.ModelAdmin):
    list_display = [
        'design_code', 'bit_type', 'size_inch', 'current_smi_name',
        'body_material', 'entry_level', 'entry_source', 'active'  # ADD entry_level, entry_source
    ]
    list_filter = [
        'bit_type', 'body_material', 'active',
        'entry_level', 'entry_source'  # ADD these filters
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('bit_type', 'size_inch', 'current_smi_name', 'hdbs_name', 'iadc_code')
        }),
        ('Entry Point', {  # ADD this section
            'fields': ('entry_level', 'entry_source', 'entry_supplier', 'entry_notes'),
            'classes': ('collapse',),
            'description': 'Specify where this design enters the manufacturing system'
        }),
        ('Design Specifications', {
            'fields': ('body_material', 'blade_count', 'cutter_size_category', 'gauge_length_inch',
                      'nozzle_count', 'port_count', 'nozzle_size', 'nozzle_port_size', 'nozzle_bore_sleeve')
        }),
        # ... rest of fieldsets
    )
```

---

## Step 4: Update BitDesignHubView

**File**: `production/views.py`

Update the `get_queryset` method to include entry level filtering:

```python
class BitDesignHubView(LoginRequiredMixin, TemplateView):
    """
    Bit Design Hub - Central junction for all bit designs
    Shows collapsible table with design + all levels (2-6)
    Now supports flexible entry levels
    """
    template_name = 'production/bitdesign_hub.html'

    def get_queryset(self):
        from django.db.models import Prefetch, Count

        qs = models.BitDesign.objects.all()

        # ---- Filters on BitDesign (design-level) ----
        search = self.request.GET.get('search')
        bit_type = self.request.GET.get('bit_type')
        body_material = self.request.GET.get('body_material')
        size_min = self.request.GET.get('size_min')
        size_max = self.request.GET.get('size_max')
        blade_count = self.request.GET.get('blade_count')
        cutter_cat = self.request.GET.get('cutter_size_category')
        connection_type = self.request.GET.get('connection_type')
        active_design = self.request.GET.get('active_design')
        
        # NEW: Entry level filters
        entry_level = self.request.GET.get('entry_level')
        entry_source = self.request.GET.get('entry_source')

        if search:
            qs = qs.filter(
                Q(current_smi_name__icontains=search) |
                Q(hdbs_name__icontains=search) |
                Q(iadc_code__icontains=search) |
                Q(design_code__icontains=search) |
                Q(design_mat_number__icontains=search) |
                Q(description__icontains=search) |
                Q(remarks__icontains=search) |
                Q(entry_supplier__icontains=search)  # NEW: search supplier
            )

        if bit_type:
            qs = qs.filter(bit_type=bit_type)

        if body_material:
            qs = qs.filter(body_material=body_material)

        if size_min:
            qs = qs.filter(size_inch__gte=size_min)

        if size_max:
            qs = qs.filter(size_inch__lte=size_max)

        if blade_count:
            qs = qs.filter(blade_count=blade_count)

        if cutter_cat:
            qs = qs.filter(cutter_size_category=cutter_cat)

        if connection_type:
            qs = qs.filter(connection_type=connection_type)

        if active_design in ['true', 'false']:
            qs = qs.filter(active=(active_design == 'true'))
            
        # NEW: Entry level filter
        if entry_level:
            qs = qs.filter(entry_level=entry_level)
            
        # NEW: Entry source filter
        if entry_source:
            qs = qs.filter(entry_source=entry_source)

        # ... rest of method unchanged
```

---

## Step 5: Update Hub Template

**File**: `production/templates/production/bitdesign_hub.html`

### 5a. Add Entry Level column to table header (after "Level" column):

```html
<thead class="table-light">
    <tr>
        <th style="width:30px;"></th>
        <th>Level</th>
        <th>Entry</th>  <!-- NEW COLUMN -->
        <th>MAT</th>
        <th>Type</th>
        <!-- ... rest of headers -->
    </tr>
</thead>
```

### 5b. Add Entry Level data in design row:

```html
<!-- Design Row (Level 1 or Entry Level) -->
<tr class="design-row" data-design-id="{{ design.pk }}" data-entry-level="{{ design.entry_level }}">
    <td>
        <i class="bi bi-caret-right-fill toggle-icon"></i>
    </td>
    <td>
        <strong>L{{ design.entry_level }}</strong>
        <small class="text-muted d-block">
            {% if design.entry_level == 1 %}Design root
            {% elif design.entry_level == 2 %}Tooling Entry
            {% elif design.entry_level == 3 %}Kit Entry
            {% elif design.entry_level == 4 %}Welded Entry
            {% elif design.entry_level == 5 %}Cutters Entry
            {% elif design.entry_level == 6 %}Ready Entry
            {% endif %}
        </small>
    </td>
    <td>
        <!-- NEW: Entry Source Badge -->
        {% if design.entry_source == 'INHOUSE' %}
            <span class="badge bg-primary" title="In-House Manufacturing">
                <i class="bi bi-building"></i> In-House
            </span>
        {% elif design.entry_source == 'PURCHASED' %}
            <span class="badge bg-warning text-dark" title="Purchased: {{ design.entry_supplier }}">
                <i class="bi bi-cart"></i> Purchased
            </span>
        {% elif design.entry_source == 'CUSTOMER' %}
            <span class="badge bg-info" title="Customer Supplied">
                <i class="bi bi-person"></i> Customer
            </span>
        {% elif design.entry_source == 'REFURB' %}
            <span class="badge bg-secondary" title="Refurbishment">
                <i class="bi bi-arrow-repeat"></i> Refurb
            </span>
        {% elif design.entry_source == 'JV' %}
            <span class="badge bg-success" title="Joint Venture: {{ design.entry_supplier }}">
                <i class="bi bi-people"></i> JV
            </span>
        {% endif %}
        {% if design.entry_supplier %}
            <small class="d-block text-muted">{{ design.entry_supplier|truncatechars:20 }}</small>
        {% endif %}
    </td>
    <td>{{ design.design_mat_number|default:"—" }}</td>
    <!-- ... rest of columns -->
</tr>
```

### 5c. Update level row to add empty Entry column:

```html
<!-- Level Rows (2-6) -->
{% for rev in design.hub_revisions %}
<tr class="level-row level-row-{{ design.pk }}">
    <td></td>
    <td>
        <strong>L{{ rev.level }}</strong>
        <!-- level description -->
    </td>
    <td></td>  <!-- Empty Entry column for level rows -->
    <td>{{ rev.mat_number }}</td>
    <!-- ... rest of columns -->
</tr>
{% endfor %}
```

---

## Step 6: Update BitDesign Create/Edit Form

**File**: `production/forms.py` (or wherever BitDesignForm is defined)

Add entry level fields to the form:

```python
class BitDesignForm(forms.ModelForm):
    class Meta:
        model = BitDesign
        fields = [
            'bit_type', 'size_inch', 'current_smi_name', 'hdbs_name', 'iadc_code',
            'entry_level', 'entry_source', 'entry_supplier', 'entry_notes',  # NEW
            'body_material', 'blade_count', 'cutter_size_category',
            # ... rest of fields
        ]
        widgets = {
            'entry_level': forms.Select(attrs={'class': 'form-select'}),
            'entry_source': forms.Select(attrs={'class': 'form-select'}),
            'entry_supplier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Supplier name (if purchased or JV)'
            }),
            'entry_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notes about entry point...'
            }),
        }
```

**File**: `production/templates/production/bitdesign_form.html`

Add entry level section to the form:

```html
<!-- Entry Point Section -->
<div class="card mb-4">
    <div class="card-header bg-info text-white">
        <h5 class="mb-0"><i class="bi bi-door-open"></i> Entry Point</h5>
    </div>
    <div class="card-body">
        <div class="row">
            <div class="col-md-6">
                <div class="mb-3">
                    <label for="id_entry_level" class="form-label">Entry Level *</label>
                    {{ form.entry_level }}
                    <div class="form-text">At which manufacturing stage does this design enter our system?</div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="mb-3">
                    <label for="id_entry_source" class="form-label">Entry Source *</label>
                    {{ form.entry_source }}
                    <div class="form-text">How is this design acquired?</div>
                </div>
            </div>
        </div>
        <div class="row" id="supplier-row" style="display: none;">
            <div class="col-md-6">
                <div class="mb-3">
                    <label for="id_entry_supplier" class="form-label">Supplier</label>
                    {{ form.entry_supplier }}
                </div>
            </div>
            <div class="col-md-6">
                <div class="mb-3">
                    <label for="id_entry_notes" class="form-label">Entry Notes</label>
                    {{ form.entry_notes }}
                </div>
            </div>
        </div>
    </div>
</div>

<!-- JavaScript to show/hide supplier field based on entry_source -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    const entrySource = document.getElementById('id_entry_source');
    const supplierRow = document.getElementById('supplier-row');
    
    function updateSupplierVisibility() {
        const value = entrySource.value;
        if (value === 'PURCHASED' || value === 'JV' || value === 'CUSTOMER') {
            supplierRow.style.display = 'flex';
        } else {
            supplierRow.style.display = 'none';
        }
    }
    
    entrySource.addEventListener('change', updateSupplierVisibility);
    updateSupplierVisibility(); // Initial state
});
</script>
```

---

## Step 7: Add Filter Dropdowns to Hub

Add entry level and entry source filters to the Hub page toolbar or filter section.

---

# VERIFICATION CHECKLIST

## Part A: UI Fixes
Run `python manage.py check` - MUST pass

On `/production/designs/hub/`:
- [ ] Table grid lines are perfectly aligned (no gaps)
- [ ] All header text and icons fully visible
- [ ] Columns button shows column names with checkboxes
- [ ] Column visibility toggle actually hides/shows columns
- [ ] Show All / Hide All buttons work
- [ ] Basic filters (if implemented) work

## Part B: Flexible Entry Levels
Run `python manage.py makemigrations` - should create migration
Run `python manage.py migrate` - MUST pass
Run `python manage.py check` - MUST pass

On `/production/designs/hub/`:
- [ ] Entry column visible in table header
- [ ] Entry level badge shows for each design
- [ ] Entry source badge (In-House/Purchased/etc.) displays correctly
- [ ] Designs with different entry levels display correctly
- [ ] Filtering by entry level works

On `/production/designs/create/`:
- [ ] Entry level dropdown appears
- [ ] Entry source dropdown appears
- [ ] Supplier field shows/hides based on source
- [ ] Can create design at any entry level

In Django Admin:
- [ ] Entry level and source visible in list
- [ ] Can filter by entry level and source
- [ ] Can edit entry level fields

---

# COMMIT MESSAGE

After completing both parts:

```
feat(production): Add flexible entry levels + fix Hub UI bugs

PART A - UI Fixes:
- Fix table grid alignment (no gaps between cells)
- Fix header content visibility
- Fix Columns button to show column visibility toggles
- Add Show All / Hide All buttons for column visibility

PART B - Flexible Entry Levels:
- Add entry_level field to BitDesign (choices: 1-6)
- Add entry_source field (INHOUSE, PURCHASED, CUSTOMER, REFURB, JV)
- Add entry_supplier and entry_notes fields
- Update Hub view with entry level column and filters
- Update BitDesign form with entry point section
- Update admin with entry level fields

This allows designs to start at any manufacturing level, supporting:
- Purchased semi-finished products
- Refurbishment workflows
- Customer-supplied components
- Joint venture partnerships

Tested: All features verified on /production/designs/hub/
```

---

# 🚨 DO NOT

1. ❌ DO NOT do minimal changes that don't fix the bugs
2. ❌ DO NOT skip any of the steps
3. ❌ DO NOT commit without testing
4. ❌ DO NOT break existing functionality
5. ❌ DO NOT remove existing features
6. ❌ DO NOT forget to create and run migrations
7. ❌ DO NOT forget to run `python manage.py collectstatic --noinput` after CSS/JS changes
