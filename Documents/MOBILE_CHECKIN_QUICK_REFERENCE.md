# Mobile Check-In System - Quick Reference

## Access the System
- **URL:** `http://yoursite.com/mobile-checkin/`
- **Requirements:** Employee must be logged in
- **Device:** Works on desktop, tablet, and mobile phones

## Key URLs

| Purpose | URL | Method |
|---------|-----|--------|
| View Check-In Dashboard | `/mobile-checkin/` | GET |
| Submit Check-In | `/mobile-checkin/checkin/` | POST |
| Submit Check-Out | `/mobile-checkin/checkout/` | POST |

## Database Fields

**Table:** `gate_attendance`

```
- employee_id (ForeignKey)
- date (DateField)
- status (CharField) → "P" for Present
- check_in_time (TimeField) → Stores HH:MM:SS
- check_out_time (TimeField) → Stores HH:MM:SS
- remarks (TextField) → Optional notes
```

## Check-In Flow

```
User Clicks Check-In
    ↓
Verify User is Logged In
    ↓
Get Current Time (Timezone Aware)
    ↓
Get/Create Attendance Record for Today
    ↓
Set check_in_time & status='P' (Present)
    ↓
Return JSON Success + Time
    ↓
Frontend Updates UI + Disables Check-In Button
    ↓
Enables Check-Out Button
```

## Check-Out Flow

```
User Clicks Check-Out
    ↓
Verify User is Logged In
    ↓
Get Current Time (Timezone Aware)
    ↓
Get Today's Attendance Record
    ↓
Set check_out_time
    ↓
Calculate Working Hours
    ↓
Return JSON Success + Times + Working Hours
    ↓
Frontend Disables Check-Out Button
```

## SQL Queries (Django ORM)

### View Today's Check-Ins by Department
```python
from django.utils import timezone
from gate.models import Attendance, Employee

today = timezone.now().date()
checkins = Attendance.objects.filter(
    date=today,
    check_in_time__isnull=False
).select_related('employee__department')

for record in checkins:
    print(f"{record.employee.full_name}: {record.check_in_time}")
```

### Find Employees Not Checked In Today
```python
from django.utils import timezone
from gate.models import Employee, Attendance

today = timezone.now().date()
all_employees = Employee.objects.filter(status='A')
checked_in = Attendance.objects.filter(
    date=today,
    check_in_time__isnull=False
).values_list('employee_id', flat=True)

not_checked = all_employees.exclude(id__in=checked_in)
```

### Calculate Working Hours for a Date
```python
from datetime import datetime, time

attendance = Attendance.objects.get(employee=emp, date=date)

if attendance.check_in_time and attendance.check_out_time:
    in_time = datetime.combine(date, attendance.check_in_time)
    out_time = datetime.combine(date, attendance.check_out_time)
    hours = (out_time - in_time).total_seconds() / 3600
```

## Frontend Events

### Check-In Button
- **Click:** Sends POST to `/mobile-checkin/checkin/`
- **Response:** Updates check-in time, disables itself, enables check-out
- **Error:** Shows red alert with error message

### Check-Out Button
- **Click:** Sends POST to `/mobile-checkin/checkout/`
- **Response:** Updates check-out time, shows working hours, disables itself
- **Error:** Shows red alert with error message

## API Response Examples

### successful Check-In
```json
{
  "status": "success",
  "message": "Checked in at 09:15:30",
  "check_in_time": "09:15:30"
}
```

### Duplicate Check-In Warning
```json
{
  "status": "warning",
  "message": "Already checked in at 09:15:30",
  "check_in_time": "09:15:30"
}
```

### Successful Check-Out
```json
{
  "status": "success",
  "message": "Checked out at 17:45:22",
  "check_out_time": "17:45:22",
  "working_hours": "8h 29m"
}
```

## Django Admin Commands

### View Today's Attendance in Shell
```bash
python manage.py shell
>>> from django.utils import timezone
>>> from gate.models import Attendance
>>> today = timezone.now().date()
>>> today_records = Attendance.objects.filter(date=today)
>>> for r in today_records:
...     print(f"{r.employee.employee_id}: {r.check_in_time} - {r.check_out_time}")
```

### Export Check-In Data to CSV
```python
import csv
from datetime import date
from gate.models import Attendance

with open('checkins.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Employee ID', 'Name', 'Date', 'Check In', 'Check Out', 'Hours'])
    
    for r in Attendance.objects.filter(date=date.today()):
        emp = r.employee
        hours = ''
        if r.check_in_time and r.check_out_time:
            from datetime import datetime, time
            in_dt = datetime.combine(r.date, r.check_in_time)
            out_dt = datetime.combine(r.date, r.check_out_time)
            hours = (out_dt - in_dt).total_seconds() / 3600
        writer.writerow([
            emp.employee_id,
            emp.full_name,
            r.date,
            r.check_in_time,
            r.check_out_time,
            hours
        ])
```

## Status Codes

| Status | Meaning | Action |
|--------|---------|--------|
| `success` | Operation successful | Update UI, proceed |
| `warning` | Already checked in/out | Show message, no UI change |
| `error` | Something went wrong | Show error, enable button again |

## Security Checklist

- ✅ Login required for all check-in views
- ✅ CSRF protection on forms
- ✅ Employee-specific data isolation
- ✅ Timezone-aware timestamps
- ✅ Database unique constraint
- ✅ Input validation
- ✅ Error handling with proper messages

## Performance

- Single query for attendance record lookup
- No N+1 queries
- Efficient unique constraint index
- Minimal JavaScript payload
- Async operations don't block UI

## Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support (iOS 12+)
- Mobile browsers: ✅ Full support

## Customization Examples

### Change Check-In Status
Edit `employee_checkin` view:
```python
attendance, created = Attendance.objects.get_or_create(
    ...,
    defaults={
        'status': 'WFH',  # Change from 'P' to 'WFH'
        ...
    }
)
```

### Add Location Capture
Modify template to capture location:
```javascript
navigator.geolocation.getCurrentPosition(function(position) {
    // Send lat/long with check-in request
});
```

### Change Button Colors
Edit CSS in template:
```css
.btn-checkin {
    background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
}
```

## Troubleshooting Checklist

| Issue | Check | Solution |
|-------|-------|----------|
| Button not clickable | Employee logged in? | Verify user has Employee record |
| Wrong time recorded | Server timezone | Check `TIME_ZONE` in settings.py |
| Can't see check-in page | Login required | User must be logged in |
| Database error | Migrations run? | Run `python manage.py migrate` |
| Times not showing | JSON response | Check browser console for errors |

## Log Locations

- Django logs: `logs/django.log` (if configured)
- Database logs: Check database error logs
- Browser console: Press F12 in browser

## Database Backup

Before testing, backup your database:
```bash
python manage.py dumpdata gate.Attendance > attendance_backup.json
```

Restore if needed:
```bash
python manage.py loaddata attendance_backup.json
```

## Testing Checklist

- [ ] Can logged-in employee see check-in page
- [ ] Can click Check-In button
- [ ] Check-In time records correctly
- [ ] Check-In button disables after click
- [ ] Check-Out button enables after Check-In
- [ ] Can click Check-Out button
- [ ] Check-Out time records correctly
- [ ] Working hours calculated correctly
- [ ] Can't check in twice same day
- [ ] Can't check out twice same day
- [ ] Works on mobile devices
- [ ] Logout button works

## Next Steps

1. **Test thoroughly** on all devices
2. **Train employees** on how to use
3. **Monitor logs** for errors
4. **Gather feedback** from users
5. **Plan enhancements** based on usage
