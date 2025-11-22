# hr/models/__init__.py
"""
HR & Administration Models - Version C
Clean architecture with separation from old repository complexity.
"""

# Core models (Person, Employee, Department, Position)
from .core import (
    HRPerson,
    HREmployee,
    Department,
    Position,
    GENDER_CHOICES,
    MARITAL_STATUS_CHOICES,
    EMPLOYMENT_STATUS_CHOICES,
    POSITION_CATEGORY_CHOICES,
)

# Employment models (Contract, Shift)
from .employment import (
    HRContract,
    HRShiftTemplate,
    CONTRACT_TYPE_CHOICES,
    SHIFT_PATTERN_CHOICES,
)

# Leave models
from .leave import (
    LeaveType,
    LeaveRequest,
    REQUEST_STATUS_CHOICES,
)

# Attendance models
from .attendance import (
    AttendanceRecord,
    ATTENDANCE_STATUS_CHOICES,
    ATTENDANCE_SOURCE_CHOICES,
)

# Training models
from .training import (
    TrainingProgram,
    TrainingSession,
    EmployeeTraining,
    TRAINING_CATEGORY_CHOICES,
    SESSION_STATUS_CHOICES,
)

# Document models
from .documents import (
    DocumentType,
    EmployeeDocument,
)

# Qualification models
from .qualifications import (
    QualificationLevel,
    EmployeeQualification,
)

# Administration/Asset models
from .administration import (
    AssetType,
    HRAsset,
    AssetAssignment,
    ASSET_STATUS_CHOICES,
)

# Contact models
from .contact import (
    HRPhone,
    HREmail,
    PHONE_TYPE_CHOICES,
    EMAIL_TYPE_CHOICES,
)

__all__ = [
    # Core
    'HRPerson',
    'HREmployee',
    'Department',
    'Position',
    # Employment
    'HRContract',
    'HRShiftTemplate',
    # Leave
    'LeaveType',
    'LeaveRequest',
    # Attendance
    'AttendanceRecord',
    # Training
    'TrainingProgram',
    'TrainingSession',
    'EmployeeTraining',
    # Documents
    'DocumentType',
    'EmployeeDocument',
    # Qualifications
    'QualificationLevel',
    'EmployeeQualification',
    # Administration
    'AssetType',
    'HRAsset',
    'AssetAssignment',
    # Contact
    'HRPhone',
    'HREmail',
    # Choices
    'GENDER_CHOICES',
    'MARITAL_STATUS_CHOICES',
    'EMPLOYMENT_STATUS_CHOICES',
    'POSITION_CATEGORY_CHOICES',
    'CONTRACT_TYPE_CHOICES',
    'SHIFT_PATTERN_CHOICES',
    'REQUEST_STATUS_CHOICES',
    'ATTENDANCE_STATUS_CHOICES',
    'ATTENDANCE_SOURCE_CHOICES',
    'TRAINING_CATEGORY_CHOICES',
    'SESSION_STATUS_CHOICES',
    'ASSET_STATUS_CHOICES',
    'PHONE_TYPE_CHOICES',
    'EMAIL_TYPE_CHOICES',
]
