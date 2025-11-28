"""
Production Department Forms
"""

from django import forms
from decimal import Decimal
from .models import BitDesign, BIT_SIZE_CHOICES


class BitDesignForm(forms.ModelForm):
    """
    Form for creating/editing BitDesign with dropdown for size selection
    """
    size_inch = forms.ChoiceField(
        choices=BIT_SIZE_CHOICES,
        help_text="Bit diameter",
        label="Size (inch)"
    )

    class Meta:
        model = BitDesign
        exclude = ['design_code']  # Hide design_code - it's auto-filled
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'remarks': forms.Textarea(attrs={'rows': 4}),
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

    def clean_size_inch(self):
        """Convert the choice value back to Decimal"""
        value = self.cleaned_data['size_inch']
        return Decimal(value)
