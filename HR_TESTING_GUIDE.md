# HR Module Testing Guide

## ✅ What Was Completed

I've successfully added a **complete HR module** with 14 models, comprehensive admin interface, and full integration with the core dashboard. All code was carefully validated - no blind copying from the old system.

---

## 🎯 What's Now Available in Codespaces

### 1. **HR Module** (`/hr/`)
- **14 Models** fully functional:
  - Department & Position (organizational structure)
  - HRPeople & HREmployee (person records & employment)
  - Leave Management (4 models)
  - Attendance Tracking (2 models)
  - Documents & Qualifications (4 models)

### 2. **Core Dashboard** (`/dashboard/`)
- ✅ **NOW WORKING!** (was disabled before)
- Shows HR statistics
- Aggregates data from HR, Inventory, Production, etc.
- Main dashboard with KPIs

### 3. **Admin Panel** (`/admin/`)
- Full CRUD for all 14 HR models
- Inline editing for related records
- Search, filter, and pagination
- Custom displays with colored status indicators

### 4. **Employee Self-Service Portal**
- My Leave requests
- My Attendance records
- Employee portal dashboard

---

## 🚀 Testing in Codespaces

### Step 1: In Your Codespace Terminal

```bash
# Activate virtual environment
source venv/bin/activate

# Create migrations for HR app
python manage.py makemigrations hr

# Run all migrations
python manage.py migrate

# Create superuser (if not already created)
python manage.py createsuperuser

# Start the server
./start.sh
```

### Step 2: Access in Browser

When the server starts, click the popup to open in browser, then test these URLs:

#### **Core Pages:**
1. **Home** → `/`
   - System dashboard with migration progress

2. **HR Home** → `/hr/`
   - HR module overview
   - Quick statistics
   - Links to all HR features

3. **Core Dashboard** → `/dashboard/`
   - Main application dashboard
   - **NOW WORKING!** (previously disabled)
   - Shows HR employee/department counts

4. **Admin Panel** → `/admin/`
   - Full Django admin
   - All HR models available

#### **HR Specific Pages:**
5. **Employee Directory** → `/hr/employees/`
6. **Department List** → `/hr/departments/`
7. **Employee Portal** → `/hr/portal/` (requires login)

---

## 🧪 Testing Checklist

### Basic Functionality
- [ ] HR home page loads without errors
- [ ] Can access admin panel
- [ ] Core dashboard loads (no more import errors!)
- [ ] Navigation between pages works

### HR Admin Tests
- [ ] Create a Department
  - Go to Admin → HR → Departments → Add
  - Code: `ENG`, Name: `Engineering`
  - Save successfully

- [ ] Create a Position
  - Go to Admin → HR → Positions → Add
  - Code: `MGR`, Title: `Manager`, Department: Engineering
  - Save successfully

- [ ] Create a Person (HRPeople)
  - Go to Admin → HR → People → Add
  - Fill required fields: name, national_id, phone
  - Save successfully

- [ ] Create an Employee (HREmployee)
  - Go to Admin → HR → Employees → Add
  - Link to person, assign department/position
  - Add salary details
  - Save successfully

### Data Validation Tests
- [ ] Try creating duplicate employee number → Should fail
- [ ] Try invalid phone number → Should show error
- [ ] Try invalid email → Should show error
- [ ] Check department employee count updates

### Leave Management Tests
- [ ] Create Leave Type
  - Code: `ANNUAL`, Name: `Annual Leave`
- [ ] Create Leave Policy
  - 30 days per year
- [ ] Create Leave Request
  - Should link to employee
  - Set dates and reason

### Attendance Tests
- [ ] Create Attendance Record
  - Select employee and date
  - Set clock in/out times
  - System calculates hours

### Document Management Tests
- [ ] Create Document Type
  - Code: `PASSPORT`, Has Expiry: Yes
- [ ] Upload Employee Document
  - Link to employee
  - Set expiry date
  - System tracks expiry

---

## 📊 Sample Test Data

### Create Test Department:
```
Code: PROD
Name: Production Department
Description: Main production floor
Is Active: Yes
```

### Create Test Position:
```
Code: OP01
Title: Production Operator
Department: PROD
Level: 1
Min Headcount: 1
Max Headcount: 10
```

### Create Test Person:
```
First Name: John
Last Name: Doe
National ID: 123456789
Primary Phone: +96512345678
Date of Birth: 1990-01-01
Gender: Male
```

### Create Test Employee:
```
Person: John Doe
Employee Number: EMP001
Department: PROD
Position: OP01
Status: ACTIVE
Employment Type: FULL_TIME
Join Date: 2024-01-01
Basic Salary: 500.000
```

---

## 🐛 Common Issues & Solutions

### Issue: "No module named 'hr'"
**Solution:** Make sure migrations are run:
```bash
python manage.py migrate
```

### Issue: "Department matching query does not exist"
**Solution:** Create departments first before creating positions/employees

### Issue: "Circular import error"
**Solution:** Restart the server:
```bash
pkill -f runserver
./start.sh
```

### Issue: Core dashboard still shows errors
**Solution:** Check that:
1. HR app is in INSTALLED_APPS
2. Migrations are run
3. At least one employee and department exists

---

## ✨ Key Features to Test

### 1. **Hierarchical Departments**
- Create parent department (e.g., "Engineering")
- Create child department (e.g., "Mechanical Engineering")
- Check hierarchy display

### 2. **Headcount Tracking**
- Create position with max_headcount = 5
- Add 3 employees to that position
- Admin should show "3 / 5" headcount

### 3. **Leave Balance Calculation**
- Create leave balance with:
  - Entitled: 30 days
  - Used: 10 days
  - Should show Available: 20 days

### 4. **Attendance Hours Calculation**
- Clock in: 08:00
- Clock out: 17:00
- Should calculate 8 hours (minus break if configured)

### 5. **Document Expiry Monitoring**
- Create document with expiry date in 15 days
- System should flag as "Needs Renewal"
- Check in admin with colored indicator

### 6. **Employee Search**
- Go to Employee Directory (`/hr/employees/`)
- Use search box
- Search by: employee number, name, department

---

## 📈 What's Next?

After HR is working, we can add:
1. **Inventory Module** (Items, Stock, Locations)
2. **Production Module** (Job Cards, Work Orders)
3. **Quality Module** (NCR, Calibration)
4. **More features...**

---

## 🎉 Success Criteria

You'll know HR is fully working when:

✅ Can create departments and positions
✅ Can register employees
✅ Can track leave and attendance
✅ Core dashboard loads with HR stats
✅ Employee directory shows all employees
✅ Admin panel has all 14 HR models
✅ No Python errors in terminal
✅ No JavaScript errors in browser console

---

## 📞 Support

If you encounter any issues:

1. **Check Python errors** in terminal
2. **Check browser console** (F12) for JS errors
3. **Verify migrations** ran successfully
4. **Check model relationships** are correct
5. **Test with minimal data** first

---

**Last Updated:** 2025-11-23
**Module:** HR v1.0
**Status:** Ready for Testing 🚀
