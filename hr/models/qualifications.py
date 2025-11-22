"""
HR Qualification Models - Version C
Employee education and certifications.
"""
from django.db import models


class QualificationLevel(models.Model):
    """Education/certification level."""

    code = models.CharField(max_length=32, unique=True, db_index=True)
    name = models.CharField(max_length=128)
    level_order = models.IntegerField(default=0, help_text="For sorting (higher = more advanced)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_qualification_level'
        verbose_name = 'Qualification Level'
        verbose_name_plural = 'Qualification Levels'
        ordering = ['level_order']

    def __str__(self):
        return f"{self.code} - {self.name}"


class EmployeeQualification(models.Model):
    """Employee education/certification."""

    employee = models.ForeignKey('HREmployee', on_delete=models.CASCADE, related_name='qualifications')
    qualification_level = models.ForeignKey(QualificationLevel, on_delete=models.PROTECT)
    field_of_study = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_employee_qualification'
        verbose_name = 'Employee Qualification'
        verbose_name_plural = 'Employee Qualifications'
        ordering = ['-completion_date']

    def __str__(self):
        return f"{self.employee.employee_no} - {self.qualification_level.name} in {self.field_of_study}"
