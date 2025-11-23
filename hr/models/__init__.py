# HR Models
from .department import Department, Position
from .people import HRPeople
from .employee import HREmployee, HRPhone, HREmail
from .leave import LeaveType, LeavePolicy, LeaveBalance, LeaveRequest
from .attendance import AttendanceRecord, OvertimeRequest
from .documents import EmployeeDocument, DocumentType
from .qualification import QualificationLevel, EmployeeQualification

__all__ = [
    # Organizational Structure
    'Department',
    'Position',

    # People & Employees
    'HRPeople',
    'HREmployee',
    'HRPhone',
    'HREmail',

    # Leave Management
    'LeaveType',
    'LeavePolicy',
    'LeaveBalance',
    'LeaveRequest',

    # Attendance
    'AttendanceRecord',
    'OvertimeRequest',

    # Documents
    'EmployeeDocument',
    'DocumentType',

    # Qualifications
    'QualificationLevel',
    'EmployeeQualification',
]
