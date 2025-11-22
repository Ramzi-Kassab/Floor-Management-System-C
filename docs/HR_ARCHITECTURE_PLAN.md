# HR & Administration Architecture Plan - Version C

**Date:** 2025-11-22
**Status:** Planning → Implementation
**Phase:** Phase 2 of Migration

---

## Executive Summary

This document outlines the clean architecture for HR & Administration domain in Floor-Management-System-C (Version C). Based on analysis of the old repository, we're designing a modern, maintainable HR system with clear separation between employee self-service and HR back-office functions.

---

## Old Repository Analysis

### What We Found in Old Repo:

**Models** (~3,060 lines across 14 files):
- HRPeople, HREmployee, Department, Position
- LeavePolicy, LeaveBalance, LeaveRequest (4 models)
- AttendanceRecord, OvertimeRequest, AttendanceSummary (5 models)
- TrainingProgram, TrainingSession, EmployeeTraining, SkillMatrix (4 models)
- EmployeeDocument, DocumentRenewal, ExpiryAlert (3 models)
- OvertimeConfiguration, AttendanceConfiguration, DelayIncident (3 models)
- HRPhone, HREmail, QualificationLevel, EmployeeQualification
- HRAuditLog (separate from core ActivityLog)

**HR Assets Module** (Administration):
- Vehicles, Phones/SIMs, Housing, Laptops assigned to employees

**Templates:** 48+ HTML files
- Organized by feature: attendance/, documents/, leave/, training/
- person_detail.html, position pages, etc.

**Issues Identified:**
- ❌ No clear separation between employee portal vs HR admin
- ❌ Some finance/ERP fields mixed into basic employee views
- ❌ HRAuditLog duplicates core ActivityLog functionality
- ❌ Some models could be simplified/merged
- ❌ No preparation for QR code integration

---

## Clean Architecture for Version C

### Principle 1: Two Distinct Apps

```
hr/                    ← HR Back-Office (Admin)
├── models/
│   ├── core.py        (Person, Employee, Department, Position)
│   ├── employment.py  (Contract, Shift)
│   ├── leave.py       (LeaveType, LeaveRequest)
│   ├── attendance.py  (AttendanceRecord)
│   ├── training.py    (TrainingProgram, TrainingSession)
│   ├── documents.py   (EmployeeDocument)
│   ├── qualifications.py
│   └── administration.py (Assets: phones, vehicles, housing)
├── views/
├── templates/hr/
└── urls.py            (namespace: /hr/)

hr_portal/             ← Employee Self-Service Portal
├── models.py          (Lightweight - mostly requests)
├── views/
│   ├── profile.py     (View my info)
│   ├── requests.py    (Leave, documents)
│   └── dashboard.py   (My portal home)
├── templates/hr_portal/
└── urls.py            (namespace: /portal/ or /me/)
```

### Principle 2: Use core_foundation Models

**Reuse from core_foundation:**
- CostCenter → Department.cost_center, Employee assignments
- Currency, ExchangeRate → Contract salary
- ApprovalType, ApprovalAuthority → Leave approvals
- Notification → Leave approved/rejected notices
- ActivityLog → Employee created, contract updated, etc.

**Group finance fields in UI:**
- Create collapsible "Finance & Cost" sections in templates
- Add feature flag: `settings.HR_SHOW_FINANCE_PANELS`
- Keep finance logic optional and hide-able

### Principle 3: Prepare for QR Integration

**QR-Friendly Design:**
- Stable primary keys (UUIDs or public_id)
- Clean URL patterns: `/hr/employees/{pk}/`
- Field placeholders for QR data (e.g., badge_qr_code)
- Comments: `# TODO-QR: Generate QR for employee badge`

**Future QR Uses:**
- Employee badges (link to profile)
- Leave request forms (QR to approve/reject)
- Asset assignments (scan QR on phone/laptop)
- Training attendance (scan to check in)

---

## Model Design - Version C

### Core Models (hr/models/core.py)

#### 1. HRPerson (Identity)

```python
class HRPerson(models.Model):
    """
    Canonical person record - pure identity, no employment data.
    Can exist before/after employment (applicants, alumni).
    """
    # Names
    first_name_en = CharField(max_length=120)
    middle_name_en = CharField(max_length=120, blank=True)
    last_name_en = CharField(max_length=120)
    first_name_ar = CharField(max_length=120, blank=True)  # Optional Arabic
    middle_name_ar = CharField(max_length=120, blank=True)
    last_name_ar = CharField(max_length=120, blank=True)

    # Identity
    national_id = CharField(max_length=64, unique=True, db_index=True)
    iqama_number = CharField(max_length=10, blank=True, db_index=True)  # For non-Saudis
    iqama_expiry = DateField(null=True, blank=True)

    # Basic Demographics
    date_of_birth = DateField(null=True, blank=True)
    gender = CharField(max_length=6, choices=[('MALE', 'Male'), ('FEMALE', 'Female')])
    nationality_iso2 = CharField(max_length=2)  # SA, US, IN, etc.
    marital_status = CharField(max_length=16, choices=MARITAL_STATUS, blank=True)

    # Photo
    photo = ImageField(upload_to='hr/people/photos/', blank=True, null=True)

    # QR Integration (future)
    # badge_qr_code = CharField(max_length=255, blank=True)  # TODO-QR

    # Audit
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_person'
        verbose_name_plural = 'HR People'
```

**Simplifications from Old Repo:**
- ✅ Removed PublicIdMixin (use standard PK or add UUID if needed)
- ✅ Removed HRSoftDeleteMixin (not needed initially - can add later)
- ✅ Removed Hijri date conversion (nice-to-have, add later if needed)
- ✅ Removed identity_verified fields (over-engineered - use ActivityLog instead)
- ✅ Simplified to essential fields only

#### 2. HREmployee (Employment Record)

```python
class HREmployee(models.Model):
    """
    Employment record linking a Person to the company.
    One Person can have multiple Employee records over time (rehire scenarios).
    """
    person = OneToOneField(HRPerson, on_delete=PROTECT, related_name='employment')
    user = OneToOneField(User, on_delete=SET_NULL, null=True, blank=True, related_name='hr_employee')

    # Employee ID
    employee_no = CharField(max_length=32, unique=True)

    # Job Assignment
    department = ForeignKey('Department', on_delete=SET_NULL, null=True, related_name='employees')
    position = ForeignKey('Position', on_delete=SET_NULL, null=True, related_name='employees')

    # Employment Status
    status = CharField(max_length=16, choices=EMPLOYMENT_STATUS, default='ACTIVE')
    # ACTIVE, ON_PROBATION, ON_LEAVE, SUSPENDED, TERMINATED, RETIRED

    # Dates
    hire_date = DateField()
    probation_end_date = DateField(null=True, blank=True)
    termination_date = DateField(null=True, blank=True)
    termination_reason = TextField(blank=True)

    # Finance Integration (hide-able in UI)
    cost_center = ForeignKey('core_foundation.CostCenter', on_delete=SET_NULL, null=True, blank=True)

    # Audit
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    created_by = ForeignKey(User, on_delete=SET_NULL, null=True, related_name='+')

    class Meta:
        db_table = 'hr_employee'
```

**Simplifications:**
- ✅ Removed duplicate status fields (STATUS vs EMPLOYMENT_STATUS - kept one)
- ✅ Removed CONTRACT_TYPE, SHIFT_PATTERN, EMPLOYMENT_CATEGORY (move to HRContract model if needed)
- ✅ Removed deprecated job_title field (use position FK)
- ✅ Removed report_to field (add later if needed for org chart)

#### 3. Department

```python
class Department(models.Model):
    """Organizational department/unit."""
    code = CharField(max_length=32, unique=True)
    name = CharField(max_length=128)
    parent = ForeignKey('self', on_delete=SET_NULL, null=True, blank=True, related_name='sub_departments')

    # Finance Integration (hide-able)
    cost_center = ForeignKey('core_foundation.CostCenter', on_delete=SET_NULL, null=True, blank=True)

    is_active = BooleanField(default=True)

    class Meta:
        db_table = 'hr_department'
        ordering = ['code']
```

#### 4. Position

```python
class Position(models.Model):
    """Job position/title in the organization."""
    code = CharField(max_length=32, unique=True)
    title = CharField(max_length=128)
    title_ar = CharField(max_length=128, blank=True)  # Arabic translation

    # Classification
    grade_level = CharField(max_length=16, blank=True)  # e.g., 'L3', 'M2', 'S1'
    category = CharField(max_length=32, choices=POSITION_CATEGORY, blank=True)
    # WORKER, TECHNICIAN, ENGINEER, SUPERVISOR, MANAGER, EXECUTIVE

    is_supervisory = BooleanField(default=False)
    is_active = BooleanField(default=True)

    class Meta:
        db_table = 'hr_position'
        ordering = ['code']
```

### Employment Models (hr/models/employment.py)

#### 5. HRContract (NEW - replaces mixed fields in old Employee)

```python
class HRContract(models.Model):
    """
    Employment contract details.
    Separate from Employee to allow contract history.
    """
    employee = ForeignKey(HREmployee, on_delete=CASCADE, related_name='contracts')

    contract_number = CharField(max_length=64, unique=True)
    contract_type = CharField(max_length=32, choices=CONTRACT_TYPE)
    # PERMANENT, FIXED_TERM, TEMPORARY, PART_TIME, INTERN, CONSULTANT, CONTRACTOR

    # Duration
    start_date = DateField()
    end_date = DateField(null=True, blank=True)  # Null for permanent

    # Compensation (hide-able in UI)
    base_salary = DecimalField(max_digits=10, decimal_places=2)
    currency = ForeignKey('core_foundation.Currency', on_delete=PROTECT)
    allowances = JSONField(default=dict, blank=True)  # {housing: 1000, transport: 500, ...}

    # Work Schedule
    working_hours_per_week = IntegerField(default=40)
    shift_pattern = CharField(max_length=32, choices=SHIFT_PATTERN, default='DAY')
    # DAY, NIGHT, ROTATING, FLEXIBLE

    notes = TextField(blank=True)
    is_active = BooleanField(default=True)

    class Meta:
        db_table = 'hr_contract'
        ordering = ['-start_date']
```

#### 6. HRShiftTemplate (Simplified from old config)

```python
class HRShiftTemplate(models.Model):
    """Reusable shift definition."""
    name = CharField(max_length=64)
    start_time = TimeField()
    end_time = TimeField()
    break_minutes = IntegerField(default=0)
    is_night_shift = BooleanField(default=False)

    class Meta:
        db_table = 'hr_shift_template'
```

### Leave Models (hr/models/leave.py)

#### 7-9. Leave System (Simplified)

```python
class LeaveType(models.Model):
    """Type of leave (Annual, Sick, Emergency, etc.)"""
    code = CharField(max_length=32, unique=True)
    name = CharField(max_length=128)
    is_paid = BooleanField(default=True)
    requires_approval = BooleanField(default=True)
    max_days_per_year = IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'hr_leave_type'

class LeaveRequest(models.Model):
    """Employee leave request."""
    employee = ForeignKey(HREmployee, on_delete=CASCADE, related_name='leave_requests')
    leave_type = ForeignKey(LeaveType, on_delete=PROTECT)

    start_date = DateField()
    end_date = DateField()
    days_count = IntegerField()  # Auto-calculated
    reason = TextField(blank=True)

    # Approval Workflow
    status = CharField(max_length=16, choices=REQUEST_STATUS, default='DRAFT')
    # DRAFT, SUBMITTED, APPROVED, REJECTED, CANCELLED

    approved_by = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True, related_name='+')
    approved_at = DateTimeField(null=True, blank=True)
    rejection_reason = TextField(blank=True)

    # Integration with core_foundation
    approval_type = ForeignKey('core_foundation.ApprovalType', on_delete=SET_NULL, null=True, blank=True)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_leave_request'
        ordering = ['-created_at']
```

**Removed from Old Repo:**
- ❌ LeaveBalance (calculate on-the-fly from requests instead)
- ❌ LeavePolicy (merged into LeaveType - simpler)
- ❌ LeaveRequestStatus (use choices on LeaveRequest)

### Attendance Models (hr/models/attendance.py)

#### 10. AttendanceRecord (Simplified)

```python
class AttendanceRecord(models.Model):
    """Daily attendance record."""
    employee = ForeignKey(HREmployee, on_delete=CASCADE, related_name='attendance_records')
    date = DateField()

    # Time Tracking
    check_in = DateTimeField(null=True, blank=True)
    check_out = DateTimeField(null=True, blank=True)

    # Status
    status = CharField(max_length=16, choices=ATTENDANCE_STATUS, default='PRESENT')
    # PRESENT, ABSENT, LATE, HALF_DAY, ON_LEAVE

    late_minutes = IntegerField(default=0)
    overtime_minutes = IntegerField(default=0)

    # Source
    source = CharField(max_length=32, default='MANUAL')
    # MANUAL, IMPORTED, WHATSAPP, TIME_CLOCK, QR_SCAN

    notes = TextField(blank=True)

    class Meta:
        db_table = 'hr_attendance_record'
        unique_together = [['employee', 'date']]
        ordering = ['-date']
```

**Removed from Old Repo:**
- ❌ AttendanceSummary (calculate on-the-fly)
- ❌ OvertimeRequest (too complex for initial version - add later if needed)
- ❌ OvertimeConfiguration, AttendanceConfiguration, DelayIncident (add later)

### Training Models (hr/models/training.py)

#### 11-13. Training System (Simplified)

```python
class TrainingProgram(models.Model):
    """Training course/program definition."""
    code = CharField(max_length=32, unique=True)
    title = CharField(max_length=200)
    description = TextField(blank=True)
    duration_hours = IntegerField()

    # Classification
    category = CharField(max_length=64, blank=True)
    # SAFETY, TECHNICAL, SOFT_SKILLS, COMPLIANCE, etc.

    is_mandatory = BooleanField(default=False)
    is_active = BooleanField(default=True)

    class Meta:
        db_table = 'hr_training_program'

class TrainingSession(models.Model):
    """Scheduled training session."""
    program = ForeignKey(TrainingProgram, on_delete=CASCADE, related_name='sessions')

    session_date = DateField()
    start_time = TimeField()
    end_time = TimeField()
    location = CharField(max_length=200, blank=True)
    trainer = CharField(max_length=200, blank=True)

    max_participants = IntegerField(null=True, blank=True)
    status = CharField(max_length=16, default='SCHEDULED')
    # SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED

    class Meta:
        db_table = 'hr_training_session'

class EmployeeTraining(models.Model):
    """Employee attendance at training session."""
    employee = ForeignKey(HREmployee, on_delete=CASCADE, related_name='training_records')
    session = ForeignKey(TrainingSession, on_delete=CASCADE, related_name='attendees')

    attended = BooleanField(default=False)
    passed = BooleanField(default=False)
    score = IntegerField(null=True, blank=True)  # If there's an exam

    certificate_issued = BooleanField(default=False)
    certificate_date = DateField(null=True, blank=True)

    # QR Integration (future)
    # attendance_qr_scanned_at = DateTimeField(null=True, blank=True)  # TODO-QR

    class Meta:
        db_table = 'hr_employee_training'
        unique_together = [['employee', 'session']]
```

**Removed:**
- ❌ SkillMatrix (too complex - add later if needed)
- ❌ TrainingType, TrainingStatus (use choices instead)

### Documents (hr/models/documents.py)

#### 14-15. Employee Documents

```python
class DocumentType(models.Model):
    """Type of employee document."""
    code = CharField(max_length=32, unique=True)
    name = CharField(max_length=128)
    requires_renewal = BooleanField(default=False)
    renewal_notice_days = IntegerField(default=30)  # Notify X days before expiry

    class Meta:
        db_table = 'hr_document_type'

class EmployeeDocument(models.Model):
    """Employee document (passport, license, certificate, etc.)"""
    employee = ForeignKey(HREmployee, on_delete=CASCADE, related_name='documents')
    document_type = ForeignKey(DocumentType, on_delete=PROTECT)

    document_number = CharField(max_length=128, blank=True)
    issue_date = DateField(null=True, blank=True)
    expiry_date = DateField(null=True, blank=True)

    file = FileField(upload_to='hr/documents/%Y/%m/', blank=True, null=True)
    notes = TextField(blank=True)

    # Status
    is_verified = BooleanField(default=False)
    verified_by = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True, related_name='+')
    verified_at = DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'hr_employee_document'
```

**Removed:**
- ❌ DocumentRenewal (auto-create from EmployeeDocument when renewed)
- ❌ ExpiryAlert (generate alerts programmatically, don't store as model)
- ❌ DocumentStatus (use choices on EmployeeDocument)

### Qualifications (hr/models/qualifications.py)

#### 16-17. Qualifications & Skills

```python
class QualificationLevel(models.Model):
    """Education/certification level."""
    code = CharField(max_length=32, unique=True)
    name = CharField(max_length=128)
    # HIGH_SCHOOL, DIPLOMA, BACHELOR, MASTER, PHD, CERTIFICATE, etc.
    level_order = IntegerField(default=0)  # For sorting

    class Meta:
        db_table = 'hr_qualification_level'
        ordering = ['level_order']

class EmployeeQualification(models.Model):
    """Employee education/certification."""
    employee = ForeignKey(HREmployee, on_delete=CASCADE, related_name='qualifications')
    qualification_level = ForeignKey(QualificationLevel, on_delete=PROTECT)

    field_of_study = CharField(max_length=200)
    institution = CharField(max_length=200)

    start_date = DateField(null=True, blank=True)
    completion_date = DateField(null=True, blank=True)

    is_verified = BooleanField(default=False)

    class Meta:
        db_table = 'hr_employee_qualification'
```

### Administration/Assets (hr/models/administration.py)

#### 18-21. HR Admin Assets (from old hr_assets module)

```python
class AssetType(models.Model):
    """Type of admin asset (Phone, Vehicle, Housing, Laptop, etc.)"""
    code = CharField(max_length=32, unique=True)
    name = CharField(max_length=128)
    requires_serial_number = BooleanField(default=False)

    class Meta:
        db_table = 'hr_asset_type'

class HRAsset(models.Model):
    """Company asset assigned to employees."""
    asset_type = ForeignKey(AssetType, on_delete=PROTECT)

    asset_number = CharField(max_length=64, unique=True)
    description = CharField(max_length=255)
    serial_number = CharField(max_length=128, blank=True)

    # Specific fields for different asset types
    # For vehicles:
    plate_number = CharField(max_length=32, blank=True)
    # For phones:
    phone_number = CharField(max_length=32, blank=True)
    sim_number = CharField(max_length=32, blank=True)
    # For housing:
    location = CharField(max_length=255, blank=True)

    status = CharField(max_length=16, choices=ASSET_STATUS, default='AVAILABLE')
    # AVAILABLE, ASSIGNED, IN_REPAIR, RETIRED

    # QR Integration (future)
    # asset_qr_code = CharField(max_length=255, blank=True)  # TODO-QR

    class Meta:
        db_table = 'hr_asset'

class AssetAssignment(models.Model):
    """Asset assignment to employee."""
    asset = ForeignKey(HRAsset, on_delete=PROTECT, related_name='assignments')
    employee = ForeignKey(HREmployee, on_delete=CASCADE, related_name='asset_assignments')

    assigned_date = DateField()
    returned_date = DateField(null=True, blank=True)

    condition_at_assignment = TextField(blank=True)
    condition_at_return = TextField(blank=True)

    notes = TextField(blank=True)

    class Meta:
        db_table = 'hr_asset_assignment'
        ordering = ['-assigned_date']
```

### Contact Information (hr/models/contact.py)

#### 22-23. Phone & Email (from old repo)

```python
class HRPhone(models.Model):
    """Phone number for a person."""
    person = ForeignKey(HRPerson, on_delete=CASCADE, related_name='phones')

    phone_number = CharField(max_length=32)
    phone_type = CharField(max_length=16, choices=PHONE_TYPE, default='MOBILE')
    # MOBILE, HOME, WORK, EMERGENCY

    is_primary = BooleanField(default=False)
    is_whatsapp = BooleanField(default=False)

    class Meta:
        db_table = 'hr_phone'

class HREmail(models.Model):
    """Email address for a person."""
    person = ForeignKey(HRPerson, on_delete=CASCADE, related_name='emails')

    email = EmailField()
    email_type = CharField(max_length=16, choices=EMAIL_TYPE, default='PERSONAL')
    # PERSONAL, WORK, OTHER

    is_primary = BooleanField(default=False)

    class Meta:
        db_table = 'hr_email'
```

---

## Portal Models (hr_portal/models.py)

### Employee Self-Service Request Model

```python
class EmployeeRequest(models.Model):
    """
    Generic employee request (letter, document, data update, etc.)
    Not leave requests - those use LeaveRequest.
    """
    employee = ForeignKey('hr.HREmployee', on_delete=CASCADE, related_name='portal_requests')

    request_type = CharField(max_length=32, choices=REQUEST_TYPE)
    # LETTER, DOCUMENT, DATA_UPDATE, CERTIFICATE, OTHER

    title = CharField(max_length=255)
    description = TextField()

    status = CharField(max_length=16, choices=REQUEST_STATUS, default='SUBMITTED')
    # SUBMITTED, IN_REVIEW, APPROVED, REJECTED, COMPLETED

    handled_by = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True, related_name='+')
    handled_at = DateTimeField(null=True, blank=True)
    response_notes = TextField(blank=True)

    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hr_portal_employee_request'
        ordering = ['-created_at']
```

---

## Model Count Summary

### Total Models in Version C: 23

**Core (6 models):**
1. HRPerson
2. HREmployee
3. Department
4. Position
5. HRContract
6. HRShiftTemplate

**Leave (2 models):**
7. LeaveType
8. LeaveRequest

**Attendance (1 model):**
9. AttendanceRecord

**Training (3 models):**
10. TrainingProgram
11. TrainingSession
12. EmployeeTraining

**Documents (2 models):**
13. DocumentType
14. EmployeeDocument

**Qualifications (2 models):**
15. QualificationLevel
16. EmployeeQualification

**Administration/Assets (3 models):**
17. AssetType
18. HRAsset
19. AssetAssignment

**Contact (2 models):**
20. HRPhone
21. HREmail

**Portal (1 model):**
22. EmployeeRequest

**From core_foundation (reused, not counted):**
- CostCenter, Currency, ExchangeRate
- ApprovalType, ApprovalAuthority
- Notification, ActivityLog

### Comparison with Old Repo:

| Aspect | Old Repo | Version C | Change |
|--------|----------|-----------|--------|
| Total models | 28 | 23 | -5 (18% reduction) |
| Total lines | ~3,060 | ~1,800 (estimated) | -41% cleaner |
| Complexity | High | Medium | Simplified |
| Separation | Mixed | Clean (2 apps) | Better architecture |

**Models Removed/Simplified:**
- ❌ LeaveBalance, LeavePolicy → Merged into LeaveType
- ❌ AttendanceSummary → Calculate on-the-fly
- ❌ OvertimeRequest, OvertimeConfiguration → Deferred (add later if needed)
- ❌ SkillMatrix → Too complex for initial version
- ❌ HRAuditLog → Use core_foundation.ActivityLog instead

---

## URL Structure

### HR Back-Office URLs (`/hr/`)

```
/hr/                                  → HR dashboard

# People & Employees
/hr/people/                           → List all people
/hr/people/<pk>/                      → Person detail
/hr/people/<pk>/edit/                 → Edit person
/hr/employees/                        → List employees
/hr/employees/<pk>/                   → Employee detail
/hr/employees/<pk>/contract/          → View/edit contracts

# Organizational Structure
/hr/departments/                      → List departments
/hr/departments/<pk>/                 → Department detail
/hr/positions/                        → List positions
/hr/positions/<pk>/                   → Position detail

# Leave Management
/hr/leave/requests/                   → All leave requests
/hr/leave/requests/<pk>/              → Leave request detail
/hr/leave/requests/<pk>/approve/      → Approve leave
/hr/leave/requests/<pk>/reject/       → Reject leave
/hr/leave/types/                      → Leave types config

# Attendance
/hr/attendance/                       → Attendance overview
/hr/attendance/records/               → All records
/hr/attendance/import/                → Import from file/WhatsApp

# Training
/hr/training/programs/                → Training programs
/hr/training/sessions/                → Scheduled sessions
/hr/training/sessions/<pk>/           → Session detail & attendees

# Documents
/hr/documents/                        → All employee documents
/hr/documents/expiring/               → Documents expiring soon

# Administration (Assets)
/hr/admin/assets/                     → All assets
/hr/admin/assets/<pk>/                → Asset detail
/hr/admin/assets/<pk>/assign/         → Assign to employee
/hr/admin/phones/                     → Quick view: phones
/hr/admin/vehicles/                   → Quick view: vehicles
/hr/admin/housing/                    → Quick view: housing
```

### Employee Portal URLs (`/portal/` or `/me/`)

```
/portal/                              → Employee dashboard

# Profile
/portal/profile/                      → My profile (view only)
/portal/profile/update-request/       → Request profile data update

# Leaves
/portal/leave/balance/                → My leave balance
/portal/leave/requests/               → My leave requests
/portal/leave/request/new/            → Submit new leave request
/portal/leave/requests/<pk>/          → My leave request detail
/portal/leave/requests/<pk>/cancel/   → Cancel pending request

# Attendance
/portal/attendance/                   → My attendance summary
/portal/attendance/this-month/        → Current month view

# Documents
/portal/documents/                    → My documents & downloads
/portal/documents/request/            → Request document/letter

# Requests
/portal/requests/                     → My general requests
/portal/requests/new/                 → Submit new request
/portal/requests/<pk>/                → Request status
```

---

## Template Structure

### HR Templates (`hr/templates/hr/`)

```
hr/templates/hr/
├── base.html                         # HR section base (extends project base.html)
├── dashboard.html                    # HR back-office dashboard
│
├── people/
│   ├── list.html
│   ├── detail.html
│   └── form.html
│
├── employees/
│   ├── list.html
│   ├── detail.html                   # With finance panel (hide-able)
│   ├── form.html
│   └── contract_form.html
│
├── departments/
│   ├── list.html
│   ├── detail.html
│   └── form.html
│
├── positions/
│   ├── list.html
│   ├── detail.html
│   └── form.html
│
├── leave/
│   ├── requests_list.html
│   ├── request_detail.html
│   ├── request_form.html
│   └── approve_modal.html
│
├── attendance/
│   ├── overview.html
│   ├── records_list.html
│   └── import_form.html
│
├── training/
│   ├── programs_list.html
│   ├── session_detail.html
│   └── attendance_form.html
│
├── documents/
│   ├── list.html
│   ├── expiring_list.html
│   └── detail.html
│
├── admin_assets/                     # Administration section
│   ├── assets_list.html
│   ├── asset_detail.html
│   ├── assign_form.html
│   ├── phones.html
│   ├── vehicles.html
│   └── housing.html
│
└── partials/
    ├── _employee_card.html
    ├── _finance_panel.html           # Collapsible finance section
    ├── _leave_status_badge.html
    └── _asset_card.html
```

### Portal Templates (`hr_portal/templates/hr_portal/`)

```
hr_portal/templates/hr_portal/
├── base.html                         # Portal base (extends project base.html)
├── dashboard.html                    # Employee portal home
│
├── profile/
│   ├── view.html
│   └── update_request_form.html
│
├── leave/
│   ├── balance.html
│   ├── requests_list.html
│   ├── request_form.html
│   └── request_detail.html
│
├── attendance/
│   ├── summary.html
│   └── monthly_view.html
│
├── documents/
│   ├── list.html
│   └── request_form.html
│
├── requests/
│   ├── list.html
│   ├── form.html
│   └── detail.html
│
└── partials/
    ├── _leave_balance_card.html
    ├── _attendance_summary_card.html
    └── _request_status_badge.html
```

---

## Finance Panel Implementation

### Finance Fields to Group:

**In Employee Detail:**
- cost_center (FK to core_foundation.CostCenter)
- Contract salary, currency, allowances

**In Department Detail:**
- cost_center

**Implementation:**

```django
{# hr/templates/hr/employees/detail.html #}

<div class="employee-details">
    <h2>{{ employee.person.full_name }}</h2>

    {# Basic Info - Always Visible #}
    <section class="basic-info">
        <p>Employee No: {{ employee.employee_no }}</p>
        <p>Department: {{ employee.department }}</p>
        <p>Position: {{ employee.position }}</p>
        <p>Status: {{ employee.get_status_display }}</p>
    </section>

    {# Finance & Cost - Collapsible/Hide-able #}
    {% if user.has_perm('hr.view_finance_info') or settings.HR_SHOW_FINANCE_PANELS %}
    <section class="finance-panel" id="finance-section">
        <h3>
            <button class="collapse-toggle" data-target="#finance-content">
                Finance & Cost Information
                <i class="icon-chevron-down"></i>
            </button>
        </h3>
        <div id="finance-content" class="collapse">
            <p>Cost Center: {{ employee.cost_center }}</p>

            {% if employee.current_contract %}
            <h4>Current Contract</h4>
            <p>Base Salary: {{ employee.current_contract.base_salary }} {{ employee.current_contract.currency }}</p>
            <p>Allowances: {{ employee.current_contract.allowances|json_pretty }}</p>
            {% endif %}

            {# Link to ERP if exists #}
            {% with employee.erp_references.first as erp %}
                {% if erp %}
                <p>ERP Reference: {{ erp.erp_document_number }}</p>
                {% endif %}
            {% endwith %}
        </div>
    </section>
    {% endif %}
</div>
```

**Feature Flag in Settings:**

```python
# settings.py
HR_SHOW_FINANCE_PANELS = config('HR_SHOW_FINANCE_PANELS', default=False, cast=bool)
```

---

## Integration with core_foundation

### 1. Notifications

```python
# When leave request is approved
from core_foundation.models import Notification

Notification.objects.create(
    user=leave_request.employee.user,
    title=f"Leave Request Approved",
    message=f"Your leave request for {leave_request.days_count} days has been approved.",
    priority='medium',
    content_object=leave_request
)
```

### 2. Activity Log

```python
# When employee is created
from core_foundation.models import ActivityLog

ActivityLog.objects.create(
    user=request.user,
    action='create',
    content_object=employee,
    changes={
        'employee_no': employee.employee_no,
        'department': str(employee.department),
        'status': employee.status
    }
)
```

### 3. Approval Workflow

```python
# Link leave request to approval type
leave_request.approval_type = ApprovalType.objects.get(code='LEAVE_APPROVAL')
leave_request.save()

# Use ApprovalAuthority to determine who can approve
authorities = ApprovalAuthority.objects.filter(
    approval_type=leave_request.approval_type,
    min_amount__lte=0,  # Leave has no amount
    max_amount__gte=0
)
```

---

## QR Code Preparation

### Fields Ready for QR:

**Employee Badge QR:**
```python
# Future addition to HREmployee:
# badge_qr_code = models.CharField(max_length=255, blank=True)
# badge_qr_generated_at = models.DateTimeField(null=True, blank=True)
```

**Leave Request QR (for approval):**
```python
# Future addition to LeaveRequest:
# approval_qr_code = models.CharField(max_length=255, blank=True)
```

**Asset QR:**
```python
# Already in HRAsset design:
# asset_qr_code = models.CharField(max_length=255, blank=True)
```

**Training Attendance QR:**
```python
# Future addition to EmployeeTraining:
# attendance_qr_scanned_at = models.DateTimeField(null=True, blank=True)
```

### URL Structure (QR-Friendly):

```
# Stable, clean URLs for QR scanning
/hr/employees/{pk}/                   # Employee profile
/hr/leave/requests/{pk}/approve/      # Approve leave via QR
/hr/admin/assets/{pk}/                # Asset detail
/hr/training/sessions/{pk}/checkin/   # Training check-in
```

**No random slugs or UUIDs in URLs** - use simple integer PKs for readability and QR efficiency.

---

## Implementation Sequence

### Phase 1: Core Models & Admin (1-2 days)

1. Create `hr` and `hr_portal` apps
2. Implement core models (Person, Employee, Department, Position, Contract)
3. Create admin interface
4. Basic views (list, detail, create, update)
5. Templates with proper namespacing

### Phase 2: Leave System (1 day)

1. LeaveType, LeaveRequest models
2. Leave request workflow (submit, approve, reject)
3. Employee portal: my leaves
4. Notification integration

### Phase 3: Attendance & Training (1 day)

1. AttendanceRecord model & views
2. Training models & session management
3. Basic reporting

### Phase 4: Documents & Assets (1 day)

1. EmployeeDocument model
2. HRAsset, AssetAssignment models
3. Administration views

### Phase 5: Polish & Documentation (0.5 day)

1. Finish documentation
2. Add comments for QR integration
3. Test all views
4. Commit to feature branch

**Total Estimated Time:** 4-5 days

---

## Success Criteria

### Functional Requirements:

- ✅ All 23 models implemented and migrated
- ✅ Clear separation: hr (back-office) vs hr_portal (self-service)
- ✅ Templates properly namespaced: `hr/employees/list.html`, `hr_portal/dashboard.html`
- ✅ Finance panels grouped and hide-able
- ✅ Integration with core_foundation (CostCenter, Notification, ActivityLog)
- ✅ QR-ready URLs and model fields (commented for future)

### Technical Requirements:

- ✅ Django check passes (0 errors)
- ✅ Migrations created successfully
- ✅ All templates render without errors
- ✅ URL namespacing correct
- ✅ No circular imports
- ✅ Code follows Django best practices

### Documentation:

- ✅ HR_ARCHITECTURE_PLAN.md (this document)
- ✅ HR_MIGRATION_SUMMARY.md (after implementation)
- ✅ Model diagrams
- ✅ URL reference
- ✅ Template reference

---

**Next Step:** Implement core models in hr/models/
