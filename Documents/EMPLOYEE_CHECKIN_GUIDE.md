# Employee Check-In/Check-Out Quick Reference

## 🎯 Quick Start Guide

### For Employees

#### Step 1: Login
```
Go to: http://localhost:8000/
Username: [Employee Username]
Password: [Employee Password]
```

#### Step 2: View Dashboard
After login, you'll see the Employee Dashboard with:
- Welcome message
- Today's Attendance section at the top
- Check-in/Check-out buttons
- Your statistics (Present Days, Absent Days, Leave Days, Total Attendance)

#### Step 3: Check-In
1. Look for the large **GREEN "CHECK IN"** button
2. Click the button
3. You'll see a success message with the timestamp
4. Your check-in time will be displayed
5. The CHECK IN button will become disabled (grayed out)
6. The CHECK OUT button will become enabled

#### Step 4: Check-Out
1. At the end of your work shift, click the **RED "CHECK OUT"** button
2. You'll see a success message with timestamp and working hours
3. Your check-out time will be displayed
4. The CHECK OUT button will become disabled
5. Your attendance record is now complete for the day

### Visual Indicators

```
┌─────────────────────────────────────────┐
│           TODAY'S ATTENDANCE            │
├─────────────────────────────────────────┤
│                                         │
│  Checked In                             │
│  ✓  Checked In                         │
│  09:12:00 AM                            │
│                ✗ Not Checked Out       │
│                09:12:00 PM              │
│                                         │
│  ┌─ CHECK IN ─┐    ┌─ CHECK OUT ─┐   │
│  │   (Green)   │    │  (Red)       │   │
│  │  DISABLED   │    │  ENABLED     │   │
│  └─────────────┘    └──────────────┘   │
│                                         │
│  ✓ Success! Checked in at 09:12:00     │
│                                         │
└─────────────────────────────────────────┘
```

## 📱 Mobile Usage

The feature is fully responsive and works on:
- ✅ Desktop computers
- ✅ Tablets
- ✅ Mobile phones (iOS/Android)

Simply access the dashboard from any device with a browser.

## 🔒 Security

- **Authentication:** Must be logged in as employee
- **CSRF Protection:** All requests are secure
- **Data Privacy:** Only your own attendance data is visible
- **Time Accuracy:** Server time is used (not device time)

## ⚙️ Tech Details

### Database Fields Updated
- `check_in_time` - Recorded when you click CHECK IN
- `check_out_time` - Recorded when you click CHECK OUT
- `status` - Set to 'P' (Present) if you check in

### API Endpoints (AJAX)
- **Check-In:** POST `/mobile-checkin/checkin/`
- **Check-Out:** POST `/mobile-checkin/checkout/`

### Response Format
```json
{
  "status": "success|warning|error",
  "message": "Descriptive message",
  "check_in_time": "09:12:00",
  "check_out_time": "17:45:30",
  "working_hours": "8h 33m"
}
```

## 🆘 Troubleshooting

### Problem: "Already checked in" message
**Solution:** You've already checked in today. Click CHECK OUT when you're ready to leave.

### Problem: "No check-in found" message for check-out
**Solution:** This happens rarely if system loses your check-in record. Admin will help resolve.

### Problem: Button is grayed out / disabled
**Solution:** 
- CHECK IN disabled = You've already checked in
- CHECK OUT disabled = You haven't checked in yet, or already checked out

### Problem: Button isn't responding
**Solutions:**
1. Check your internet connection
2. Refresh the page
3. Try again
4. Contact admin if issue persists

## 📊 Working Hours Calculation

Working hours are automatically calculated as:
```
Working Hours = Check-Out Time - Check-In Time
Example: 17:45 - 09:15 = 8 hours 30 minutes
```

## 🕐 Time Display

All times are shown in:
- **Format:** HH:MM:SS (24-hour format)
- **Timezone:** Server timezone
- **Example:** 09:15:30 AM displays as 09:15:30

## 📋 Attendance Report

Your attendance record is automatically saved with:
- ✅ Employee ID
- ✅ Date
- ✅ Check-in time
- ✅ Check-out time
- ✅ Working hours
- ✅ Status (Present)

Access your complete attendance history:
→ Employee Dashboard → Quick Actions → View My Attendance Calendar

## 🔄 Daily Reset

The check-in/check-out status resets every day at 00:00 (midnight):
- Next day's buttons will be enabled
- Previous day's record is saved
- No need to manual reset

## 👥 For Multiple Employees

Each employee has:
- Individual login credentials
- Personal dashboard
- Personal attendance records
- Private check-in/check-out buttons

## 💡 Tips & Best Practices

1. **Check-in immediately** upon arriving at office
2. **Check-out exactly** when leaving the office
3. **Take screenshots** if important (for records)
4. **Notify admin** if you forgot to check out
5. **Use consistent timing** for accurate reports

## 📞 Support

For issues or questions:
- Contact your office administrator
- Email: [Admin Email]
- Phone: [Admin Phone]
- Portal: [Help Desk URL]

---

**Last Updated:** March 7, 2026
**Version:** 1.0
**Status:** Active ✅
