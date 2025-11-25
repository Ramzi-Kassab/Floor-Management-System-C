# Bit Design Hub Implementation - Remaining Tasks

## CRITICAL: This session ran out of context during comprehensive implementation

### Completed:
1. ✅ Added "Bit Design Hub" to navbar (Bit Management dropdown)
2. ✅ Added Bit Design Hub card to dashboard
3. ✅ Updated BitType choices: PDC='FC', RC='RC'
4. ✅ Updated BodyMaterial choices: short labels (Matrix, Steel)
5. ✅ Added choice constants:
   - BIT_SUBCATEGORY_CHOICES
   - API_CONNECTION_SIZE_CHOICES
   - CONNECTION_END_TYPE_CHOICES
   - DRIFT_TYPE_CHOICES
   - BIT_SIZE_CHOICES

### Still Required (PRIORITY ORDER):

#### 1. BitDesign Model - Add New Fields (HIGH PRIORITY)
Add to `production/models.py` in BitDesign:

```python
# After existing fields, add:

bit_subcategory = models.CharField(
    max_length=20,
    choices=BIT_SUBCATEGORY_CHOICES,
    blank=True,
    null=True,
    help_text="Bit subcategory (Standard FC, Core head, RC)"
)

connection_size = models.CharField(
    max_length=20,
    choices=API_CONNECTION_SIZE_CHOICES,
    blank=True,
    null=True,
    help_text="Bit connection size (API REG/IF/FH)"
)

connection_end_type = models.CharField(
    max_length=3,
    choices=CONNECTION_END_TYPE_CHOICES,
    default="PIN",
    help_text="Pin (external) or Box (internal)"
)

drift_type = models.CharField(
    max_length=12,
    choices=DRIFT_TYPE_CHOICES,
    blank=True,
    null=True,
    help_text="Internal bore: standard or full drift"
)

nozzle_port_size = models.CharField(
    max_length=20,
    blank=True,
    null=True,
    help_text="Nozzle port/pocket size"
)

nozzle_size = models.CharField(
    max_length=20,
    blank=True,
    null=True,
    help_text="Nozzle orifice size (e.g. 12/32)"
)

nozzle_bore_sleeve = models.BooleanField(
    blank=True,
    null=True,
    help_text="Nozzle bore sleeve used?"
)

# Make design_code editable=False
design_code = models.CharField(
    max_length=50,
    unique=True,
    db_index=True,
    editable=False,  # ADD THIS
    help_text="Auto-filled from SMI/HDBS name"
)
```

Auto-fill design_code in `BitDesign.save()`:
```python
if not self.design_code:
    self.design_code = self.current_smi_name or self.hdbs_name or f"DESIGN-{uuid.uuid4().hex[:8].upper()}"
```

#### 2. BitDesignRevision - Add Variant Fields (HIGH PRIORITY)

```python
variant_label = models.CharField(
    max_length=100,
    blank=True,
    help_text="Short label (e.g. 'Texas L3 kit', 'ALT cutter set')"
)

variant_notes = models.TextField(
    blank=True,
    help_text="What distinguishes this MAT from other variants"
)
```

#### 3. Template Filters (HIGH PRIORITY)
Create `production/templatetags/bit_format.py`:

```python
from django import template
from decimal import Decimal

register = template.Library()

BIT_SIZE_MAP = {
    Decimal("3.625"): '3 5/8"',
    Decimal("3.75"): '3 3/4"',
    Decimal("3.875"): '3 7/8"',
    Decimal("5.5"): '5 1/2"',
    Decimal("5.875"): '5 7/8"',
    Decimal("6"): '6"',
    Decimal("6.125"): '6 1/8"',
    Decimal("6.25"): '6 1/4"',
    Decimal("8.375"): '8 3/8"',
    Decimal("8.5"): '8 1/2"',
    Decimal("12"): '12"',
    Decimal("12.25"): '12 1/4"',
    Decimal("14.5"): '14 1/2"',
    Decimal("16"): '16"',
    Decimal("17"): '17"',
    Decimal("17.5"): '17 1/2"',
    Decimal("22"): '22"',
    Decimal("24"): '24"',
    Decimal("27"): '27"',
    Decimal("28"): '28"',
    Decimal("34"): '34"',
}

@register.filter
def bit_size_display(value):
    """Display bit size with fraction labels"""
    if not value:
        return "—"
    try:
        dec_val = Decimal(str(value))
        return BIT_SIZE_MAP.get(dec_val, f'{float(dec_val):.2f}"'.rstrip('0').rstrip('.') + '"')
    except:
        return str(value)

@register.filter
def length_display(value):
    """Display length cleanly (no .000)"""
    if not value:
        return "—"
    try:
        fval = float(value)
        if fval == int(fval):
            return str(int(fval))
        return f'{fval:.2f}'.rstrip('0').rstrip('.')
    except:
        return str(value)
```

#### 4. Clone/Branch Views (MEDIUM PRIORITY)

Create in `production/views.py`:

```python
class BitMatCloneAsBranchView(LoginRequiredMixin, CreateView):
    """Clone MAT as same-level branch"""
    model = models.BitDesignRevision
    template_name = 'production/bitmat_clone_form.html'
    fields = ['mat_number', 'variant_label', 'variant_notes', 'upper_welded', 'effective_from', 'effective_to', 'active', 'remarks']

    def get_initial(self):
        source = get_object_or_404(models.BitDesignRevision, pk=self.kwargs['pk'])
        return {
            'level': source.level,
            'previous_level': source.previous_level,
            'upper_welded': source.upper_welded,
            'variant_label': source.variant_label,
            'active': True,
        }

    def form_valid(self, form):
        source = get_object_or_404(models.BitDesignRevision, pk=self.kwargs['pk'])
        form.instance.design = source.design
        form.instance.level = source.level
        form.instance.previous_level = source.previous_level
        messages.success(self.request, f'Branch MAT {form.instance.mat_number} created at Level {source.level}')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('production:bitdesign-hub') + f'?search={self.object.design.design_code}'
```

Add URL:
```python
path('mats/<int:pk>/clone-branch/', views.BitMatCloneAsBranchView.as_view(), name='mat-clone-branch'),
```

#### 5. Update Templates - Hide design_code (MEDIUM PRIORITY)

Remove `design_code` from:
- `bitdesign_form.html` (already not in field list if editable=False)
- `bitdesign_detail.html` - remove the display
- `bitdesign_list.html` - already not shown
- `bitdesign_hub.html` - already not shown

#### 6. Update Hub Template (MEDIUM PRIORITY)

In `bitdesign_hub.html`:
- Add columns for new fields (connection_size, nozzle_size, etc.)
- Use {% load bit_format %} and apply |bit_size_display and |length_display filters
- Show variant_label in level rows
- Add "Clone as branch" action in level row dropdown
- Improve styling with better Bootstrap spacing

#### 7. Update Forms (MEDIUM PRIORITY)

Create `production/forms.py`:

```python
from django import forms
from .models import BitDesign, BIT_SIZE_CHOICES

class BitDesignForm(forms.ModelForm):
    size_inch = forms.ChoiceField(
        choices=BIT_SIZE_CHOICES,
        help_text="Bit diameter"
    )

    class Meta:
        model = BitDesign
        exclude = ['design_code']  # Hide design_code

    def clean_size_inch(self):
        return Decimal(self.cleaned_data['size_inch'])
```

Use in views:
```python
class BitDesignCreateView(LoginRequiredMixin, CreateView):
    model = models.BitDesign
    form_class = BitDesignForm
    ...
```

#### 8. Migrations

```bash
python manage.py makemigrations production
python manage.py migrate
```

## FILE CHECKLIST

| File | Changes Needed |
|------|----------------|
| `production/models.py` | ✅ Choices updated, ⏳ Add 7 new fields to BitDesign, ⏳ Add 2 to BitDesignRevision, ⏳ Update save() |
| `production/templatetags/bit_format.py` | ⏳ CREATE NEW |
| `production/forms.py` | ⏳ CREATE NEW |
| `production/views.py` | ⏳ Add BitMatCloneAsBranchView, ⏳ Update create/update views to use form |
| `production/urls.py` | ⏳ Add clone-branch URL |
| `production/admin.py` | ⏳ Add new fields to fieldsets |
| `production/templates/production/bitdesign_hub.html` | ⏳ Major update with new columns, filters, styling |
| `production/templates/production/bitdesign_form.html` | ⏳ Group fields into sections |
| `production/templates/production/bitdesign_detail.html` | ⏳ Remove design_code, add new fields |
| `production/templates/production/bitmat_clone_form.html` | ⏳ CREATE NEW |

## NEXT SESSION COMMAND

```
Continue implementing Bit Design Hub enhancements from IMPLEMENTATION_TODO.md.
Start with:
1. Add 7 new fields to BitDesign model
2. Add 2 variant fields to BitDesignRevision
3. Create template filters
4. Create migrations
Then proceed with remaining tasks in priority order.
```

