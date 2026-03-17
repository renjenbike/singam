# Salary Structure Auto-Calculation - Quick Reference Guide

## 🎯 Feature Overview
Automatic salary calculation based on Basic Salary with zero manual input errors.

## 📝 How to Use

### Access the Feature
```
Path: /salary-structure/?employee_id=<employee_id>
```

### Step 1: Enter Basic Salary
- Navigate to employee's salary structure page
- Enter the **Basic Salary** amount
- All other values calculate instantly

### Step 2: Optional Adjustments
- **Other Allowances**: Add additional allowances beyond the 2% calculated
- **Other Deductions**: Add special deductions (loans, advances, etc.)

### Step 3: Save
- Click "Save Salary Structure"
- Values persist in database

---

## 💰 Salary Components

### Auto-Calculated from Basic Salary
| Component | Amount |
|-----------|--------|
| HRA | 40% of Basic |
| DA (Dearness Allowance) | 10% of Basic |
| Conveyance | 5% of Basic |
| Medical Allowance | 3% of Basic |
| **Subtotal (Other Earnings)** | **2% of Basic** |

### Auto-Calculated from Gross Salary
| Component | Amount |
|-----------|--------|
| PF Contribution | 12% of Basic |
| ESI Contribution | 0.75% of Gross |
| Income Tax | 5% of Gross |

### Manual Entry Allowed
| Component |
|-----------|
| Other Allowances (additional) |
| Other Deductions |

---

## 📊 Example Calculation

### Input
**Basic Salary: ₹50,000**

### Auto-Calculated Earnings
- HRA: ₹50,000 × 40% = ₹20,000
- DA: ₹50,000 × 10% = ₹5,000
- Conveyance: ₹50,000 × 5% = ₹2,500
- Medical: ₹50,000 × 3% = ₹1,500
- Other: ₹50,000 × 2% = ₹1,000

**Gross Salary: ₹80,000**

### Auto-Calculated Deductions
- PF: ₹50,000 × 12% = ₹6,000
- ESI: ₹80,000 × 0.75% = ₹600
- Income Tax: ₹80,000 × 5% = ₹4,000
- Other Deductions: ₹0 (or manual entry)

**Total Deductions: ₹10,600**

### Final Salary
**Net Salary (Take Home): ₹69,400**

---

## ⚙️ Field Status

### 🟢 Editable Fields
- ✏️ Basic Salary (Required)
- ✏️ Other Allowances (Optional)
- ✏️ Other Deductions (Optional)

### ⚫ Read-Only Fields (Auto-Calculated)
- 🔒 HRA
- 🔒 DA
- 🔒 Conveyance
- 🔒 Medical Allowance
- 🔒 PF Contribution
- 🔒 ESI Contribution
- 🔒 Income Tax

---

## 🚀 Real-Time Updates

All calculations update **instantly** as you type in the Basic Salary field. No page refresh needed!

---

## 💾 Data Persistence

- All values are saved to database when form is submitted
- Calculations are recalculated when page loads
- Existing salary data is preserved

---

## 📋 Troubleshooting

| Issue | Solution |
|-------|----------|
| Values not calculating | Check if JavaScript is enabled |
| Read-only fields editable | Clear browser cache and refresh |
| Numbers showing as 0 | Ensure basic salary field has a value |
| Old values persisting | Clear browser cache |

---

## 🔧 Technical Details

- **Framework**: Django 5.x
- **Frontend**: Vanilla JavaScript
- **Storage**: SQLite Database
- **Calculation Type**: Real-time client-side
- **No API Calls**: Calculations happen locally

---

## 📱 Browser Support

Works on all modern browsers:
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Opera

(Requires JavaScript enabled)

---

## 📞 Support

**For feature issues:**
1. Refresh the page
2. Clear browser cache
3. Try in a different browser
4. Check browser console for JavaScript errors

---

**Last Updated**: March 7, 2026
**Version**: 1.0
**Status**: Production Ready
