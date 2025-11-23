"""
Department and Position models for organizational structure.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Department(models.Model):
    """
    Represents a department in the organization.
    Supports hierarchical structure with parent departments.
    """
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text='Unique department code'
    )
    name = models.CharField(
        max_length=100,
        help_text='Department name'
    )
    description = models.TextField(
        blank=True,
        help_text='Department description and responsibilities'
    )

    # Hierarchical structure
    parent_department = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_departments',
        help_text='Parent department for organizational hierarchy'
    )

    # Department head
    department_head = models.ForeignKey(
        'HREmployee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
        help_text='Employee who heads this department'
    )

    # Financial linkage
    cost_center = models.ForeignKey(
        'core_foundation.CostCenter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departments',
        help_text='Associated cost center for financial tracking'
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this department is currently active'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_departments'
    )

    class Meta:
        db_table = 'hr_department'
        ordering = ['code']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def get_full_hierarchy(self):
        """Returns full department hierarchy path."""
        hierarchy = [self.name]
        parent = self.parent_department
        while parent:
            hierarchy.insert(0, parent.name)
            parent = parent.parent_department
        return ' > '.join(hierarchy)

    def get_all_sub_departments(self):
        """Returns all sub-departments recursively."""
        sub_depts = list(self.sub_departments.all())
        for sub_dept in list(sub_depts):
            sub_depts.extend(sub_dept.get_all_sub_departments())
        return sub_depts

    def get_employee_count(self):
        """Returns number of employees in this department."""
        return self.employees.filter(is_deleted=False).count()


class Position(models.Model):
    """
    Represents a job position/role in the organization.
    """
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text='Unique position code'
    )
    title = models.CharField(
        max_length=100,
        help_text='Position title'
    )
    description = models.TextField(
        blank=True,
        help_text='Position description and responsibilities'
    )

    # Department linkage
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='positions',
        help_text='Department this position belongs to'
    )

    # Position hierarchy
    reports_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports',
        help_text='Position this role reports to'
    )

    # Position level
    level = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Position level in organizational hierarchy (1=lowest)'
    )

    # Headcount
    min_headcount = models.IntegerField(
        default=1,
        validators=[MinValueValidator(0)],
        help_text='Minimum required headcount for this position'
    )
    max_headcount = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Maximum allowed headcount for this position'
    )

    # Requirements
    required_qualifications = models.TextField(
        blank=True,
        help_text='Required qualifications for this position'
    )
    required_skills = models.TextField(
        blank=True,
        help_text='Required skills for this position'
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this position is currently active'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_positions'
    )

    class Meta:
        db_table = 'hr_position'
        ordering = ['department__code', 'code']
        verbose_name = 'Position'
        verbose_name_plural = 'Positions'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['title']),
            models.Index(fields=['department', 'is_active']),
        ]

    def __str__(self):
        return f"{self.code} - {self.title} ({self.department.code})"

    def get_current_headcount(self):
        """Returns current number of employees in this position."""
        return self.employees.filter(is_deleted=False).count()

    def is_headcount_within_limits(self):
        """Checks if current headcount is within defined limits."""
        current = self.get_current_headcount()
        return self.min_headcount <= current <= self.max_headcount

    def get_vacancy_count(self):
        """Returns number of vacancies for this position."""
        current = self.get_current_headcount()
        return max(0, self.max_headcount - current)
