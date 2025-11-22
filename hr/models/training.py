"""
HR Training Models - Version C
Training programs, sessions, and employee training records.
"""
from django.db import models


TRAINING_CATEGORY_CHOICES = [
    ('SAFETY', 'Safety Training'),
    ('TECHNICAL', 'Technical Training'),
    ('SOFT_SKILLS', 'Soft Skills'),
    ('COMPLIANCE', 'Compliance'),
    ('LEADERSHIP', 'Leadership'),
    ('OTHER', 'Other'),
]

SESSION_STATUS_CHOICES = [
    ('SCHEDULED', 'Scheduled'),
    ('IN_PROGRESS', 'In Progress'),
    ('COMPLETED', 'Completed'),
    ('CANCELLED', 'Cancelled'),
]


class TrainingProgram(models.Model):
    """Training course/program definition."""

    code = models.CharField(max_length=32, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_hours = models.IntegerField()
    category = models.CharField(max_length=64, choices=TRAINING_CATEGORY_CHOICES, blank=True)
    is_mandatory = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_training_program'
        verbose_name = 'Training Program'
        verbose_name_plural = 'Training Programs'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.title}"


class TrainingSession(models.Model):
    """Scheduled training session."""

    program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name='sessions')
    session_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=200, blank=True)
    trainer = models.CharField(max_length=200, blank=True)
    max_participants = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=SESSION_STATUS_CHOICES, default='SCHEDULED')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_training_session'
        verbose_name = 'Training Session'
        verbose_name_plural = 'Training Sessions'
        ordering = ['-session_date']

    def __str__(self):
        return f"{self.program.title} - {self.session_date}"


class EmployeeTraining(models.Model):
    """Employee attendance at training session."""

    employee = models.ForeignKey('HREmployee', on_delete=models.CASCADE, related_name='training_records')
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='attendees')
    attended = models.BooleanField(default=False)
    passed = models.BooleanField(default=False)
    score = models.IntegerField(null=True, blank=True)
    certificate_issued = models.BooleanField(default=False)
    certificate_date = models.DateField(null=True, blank=True)

    # QR Integration (future)
    # attendance_qr_scanned_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_employee_training'
        verbose_name = 'Employee Training Record'
        verbose_name_plural = 'Employee Training Records'
        unique_together = [['employee', 'session']]

    def __str__(self):
        return f"{self.employee.employee_no} - {self.session.program.title}"
