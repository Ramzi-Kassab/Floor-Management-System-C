# Shop Floor User Guide
## Printable Job Cards & QR Code Scanning System

*Quick reference guide for operators and supervisors*

---

## 📋 For Supervisors: Printing Job Cards

### Step 1: Access the Job Card
1. Navigate to **Production** → **Job Cards**
2. Click on the job card you want to print
3. You'll see the job card details page

### Step 2: Print the Route Sheet
1. Click the **"Print Route Sheet"** button (blue button with printer icon)
2. A new window opens with the printable route sheet
3. Review the route sheet:
   - Job card information (WO number, customer, priority)
   - All process steps in sequence
   - QR code for each process step
   - Status badges (Pending, In Progress, Done)
   - Operator signature fields

### Step 3: Print and Attach
1. Click **"Print Job Card"** button at the top
2. Ensure QR codes are clearly visible in the print preview
3. Print the route sheet
4. Attach it to the physical job card or bit
5. Place in the production queue

---

## 📱 For Operators: QR Code Scanning Workflow

### What You Need
- Your registered phone number (contact HR if not registered)
- The printed job card route sheet with QR codes
- A smartphone or tablet with camera/QR scanner

### How to Scan QR Codes

#### Method 1: Using Phone's Camera
1. Open your phone's camera app
2. Point at the QR code for your process step
3. A notification appears with a link
4. **IMPORTANT:** Before opening the link, add your phone number:
   - If the link is: `http://system/production/qr/JC-xxx-STEP-1/`
   - Open it as: `http://system/production/qr/JC-xxx-STEP-1/?phone=+966501234567`
   - Replace `+966501234567` with your actual phone number

#### Method 2: Using QR Scanner App
1. Download a QR scanner app (if needed)
2. Scan the QR code
3. Add `?phone=YOUR_NUMBER` to the URL before opening
4. Open the link

#### Method 3: Pre-Login (Recommended)
1. Log into the system on your phone once
2. Go to **Production** → **Dashboard**
3. Your phone number is saved in the session
4. Now you can scan QR codes directly without adding phone number each time

---

## 🔄 The Dual-Scan Process

### FIRST SCAN → Start the Process

1. **Find your process step** on the printed route sheet
   - Make sure it's the correct sequence (check step number)
   - Status should show "PENDING" (yellow badge)

2. **Scan the QR code** for that step
   - Include your phone number (see methods above)
   - Wait for the system to load

3. **System Response - SUCCESS:**
   ```
   ✓ Process STARTED by Ahmed Al-Saudi
   Process: LATHE-001
   Scan again when finished to complete.
   ```
   - The status changes to "IN PROGRESS" (blue badge)
   - Your name is recorded
   - Start time is recorded
   - You can now begin the manufacturing operation

4. **System Response - ERROR (Wrong Sequence):**
   ```
   ⚠️ WRONG PROCESS SCANNED!
   You scanned: MILL-002
   Expected next step: LATHE-001

   Please scan the correct QR code or submit a correction request.
   ```
   - You scanned the wrong process (out of sequence)
   - Scan the correct process as indicated
   - If you already started the wrong process, submit a correction request

### PERFORM THE WORK

- Complete the manufacturing operation as required
- Follow all safety procedures
- Use the correct tools and parameters
- Perform quality checks as specified

### SECOND SCAN → Complete the Process

1. **Scan the SAME QR code again**
   - Same process step you started
   - No need to add phone number again (already in session)

2. **System Response - SUCCESS:**
   ```
   ✓ Process COMPLETED by Ahmed Al-Saudi
   Process: LATHE-001
   Duration: 45 minutes
   ```
   - The status changes to "DONE" (green badge)
   - End time is recorded
   - Duration is calculated automatically
   - Your performance metric is saved for analytics

3. **System Response - ERROR (Operator Mismatch):**
   ```
   ⚠️ OPERATOR MISMATCH!
   This process was started by: Mohammed Al-Otaibi
   You are: Ahmed Al-Saudi

   Only the operator who started can complete it.
   ```
   - Someone else started this process
   - Only they can complete it
   - If the original operator is unavailable, supervisor must submit correction request

4. **System Response - INFO (Already Completed):**
   ```
   ℹ️ This process is already COMPLETED.
   Process: LATHE-001
   Completed by: Ahmed Al-Saudi
   ```
   - This process is already done
   - No action needed
   - Move to the next process step

---

## ✅ Best Practices

### DO:
✅ **Always scan in sequence** - Follow the step numbers on the route sheet
✅ **Scan to start, then scan to complete** - Two scans per process
✅ **Include your phone number** on first scan (or pre-login)
✅ **Check the success message** before starting work
✅ **Complete what you start** - Don't leave processes in "In Progress"
✅ **Sign the physical route sheet** after completing each step

### DON'T:
❌ **Don't skip processes** - System validates sequence
❌ **Don't scan someone else's process** - System tracks operators
❌ **Don't scan multiple times** by accident - Wait for confirmation
❌ **Don't complete someone else's process** - Operator mismatch error
❌ **Don't forget to scan** - Time tracking depends on scans

---

## 🔧 Troubleshooting

### Problem: "Phone number not registered"
**Solution:**
- Contact HR or your supervisor
- They will add your phone number to the system
- Phone numbers must be unique

### Problem: "QR code has expired"
**Solution:**
- QR codes can be set to expire for security
- Ask supervisor to regenerate the job card
- Print a new route sheet

### Problem: "Wrong process scanned"
**Solution:**
- Check the route sheet for the correct sequence
- Scan the process indicated in the error message
- If you already started the wrong process, submit a correction request

### Problem: "Operator mismatch"
**Scenario:** Ahmed started the process, but Mohammed is trying to complete it
**Solutions:**
1. **Find Ahmed** to complete the process he started
2. **Supervisor intervention:** Supervisor can submit a correction request to reassign
3. **Emergency:** Contact production supervisor immediately

### Problem: "Already completed"
**Solution:**
- This process is done, move to the next step
- Check the route sheet for the next pending process
- If you believe this is an error, notify supervisor

### Problem: Can't scan QR code (blurry, damaged)
**Solution:**
- Ensure good lighting
- Hold phone steady
- Clean the printed QR code if dirty
- If QR code is damaged, ask supervisor to reprint route sheet
- Supervisor can manually enter the QR code: `/production/qr/CODE/`

---

## 📞 Who to Contact

| Issue | Contact |
|-------|---------|
| Phone number not registered | HR Department |
| Wrong process sequence | Production Supervisor |
| Operator mismatch | Production Supervisor |
| QR code damaged/unreadable | Production Supervisor (reprint) |
| Technical system errors | IT Support |
| Quality issues | QC Department |
| Process correction needed | Production Supervisor (correction request) |

---

## 📊 Understanding Status Badges

| Badge Color | Status | Meaning | Action |
|------------|--------|---------|--------|
| 🟨 Yellow | **PENDING** | Not started yet | Scan to START |
| 🟦 Blue | **IN PROGRESS** | Currently being worked on | Complete the work, then scan to COMPLETE |
| 🟩 Green | **DONE** | Completed | Move to next step |

---

## 🎯 Example: Complete Workflow

**Scenario:** Ahmed is assigned to complete LATHE-001 process on Job Card JC-2025-001

### Step 1: Receive Job Card
- Supervisor prints route sheet
- Ahmed receives the printed route sheet
- Ahmed checks: First step is LATHE-001 (Status: PENDING)

### Step 2: Start Process
- Ahmed scans QR code with phone: `/production/qr/JC-2025-001-STEP-1/?phone=+966501234567`
- System shows: ✓ Process STARTED by Ahmed Al-Saudi
- Status changes to IN PROGRESS
- Start time: 08:30 AM

### Step 3: Perform Work
- Ahmed sets up the lathe
- Follows work instructions
- Completes the machining operation
- Performs visual inspection

### Step 4: Complete Process
- Ahmed scans the same QR code again: `/production/qr/JC-2025-001-STEP-1/`
- System shows: ✓ Process COMPLETED by Ahmed Al-Saudi - Duration: 45 minutes
- Status changes to DONE
- End time: 09:15 AM
- Ahmed signs the physical route sheet

### Step 5: Move to Next Process
- Ahmed checks route sheet for next step: MILL-002
- MILL-002 status is now PENDING (automatically became the next step)
- If Ahmed is trained for MILL-002, he continues
- Otherwise, he passes the job card to the next department

---

## 🌐 Language Support

The system supports both English and Arabic:

- **To switch language:** Click the language dropdown in the top navigation
- **Arabic mode:** All interface text appears in Arabic, layout switches to RTL (right-to-left)
- **English mode:** Default left-to-right layout

The printed route sheets automatically adapt to the selected language.

---

## 📱 Mobile Tips

### For Best Mobile Experience:

1. **Use landscape mode** for better visibility of route sheets
2. **Increase screen brightness** for better QR code scanning
3. **Clean your camera lens** for faster scanning
4. **Bookmark the dashboard** for quick access
5. **Enable auto-login** (if supported) to avoid repeated logins

### Recommended Browsers:
- ✅ Google Chrome (Android)
- ✅ Safari (iPhone)
- ✅ Microsoft Edge
- ❌ Avoid old browsers (IE11, etc.)

---

## 🔒 Data Privacy & Security

- Your phone number is used **only** for operator recognition
- Scan data includes: operator name, timestamps, process codes
- All data is stored securely in the company database
- Only authorized supervisors can view operator performance
- Your personal phone is NOT stored, only the number
- Contact IT if you need to update your phone number

---

## 📈 Performance Metrics

Your scans contribute to important metrics:

- **Process Time Tracking:** How long each operation takes
- **Operator Efficiency:** Your average time per process
- **Quality Metrics:** Correlation between operator and quality results
- **Department KPIs:** Overall production performance

**Note:** These metrics are used for continuous improvement, not for punishment. They help identify training needs, process bottlenecks, and efficiency opportunities.

---

## 🎓 Training Resources

### New Operator Onboarding:
1. Shadow an experienced operator for one shift
2. Practice scanning QR codes on training job cards
3. Learn to interpret status badges and error messages
4. Understand the dual-scan workflow
5. Know when to contact supervisor

### Quick Reference Card:
Print and laminate this workflow:

```
┌─────────────────────────────────┐
│  QR SCANNING QUICK GUIDE        │
├─────────────────────────────────┤
│ 1️⃣ FIRST SCAN → START           │
│    ✓ Check sequence             │
│    ✓ Add phone number           │
│    ✓ Wait for confirmation      │
│                                 │
│ 2️⃣ DO THE WORK                  │
│    ✓ Follow procedures          │
│    ✓ Use correct tools          │
│    ✓ Check quality              │
│                                 │
│ 3️⃣ SECOND SCAN → COMPLETE       │
│    ✓ Scan SAME QR code          │
│    ✓ Wait for confirmation      │
│    ✓ Sign route sheet           │
│                                 │
│ ⚠️ ERRORS? Contact Supervisor   │
└─────────────────────────────────┘
```

---

**Version:** 1.0
**Last Updated:** 2025-11-23
**Questions?** Contact your production supervisor or IT support

