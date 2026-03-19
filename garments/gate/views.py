from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum, Count
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from calendar import monthcalendar, month_name
import calendar

from .models import (
    Employee, Attendance, Leave, SalaryStructure, PayrollMonth, 
    PayrollRecord, SalarySlip, Department, Deduction, HolidayCalendar,
    DailySalarySlip
)

# ============= DASHBOARD VIEWS =============

@login_required
def dashboard(request):
    """Main dashboard - role-based redirect"""
    try:
        employee = Employee.objects.get(user=request.user)
        return redirect('employee_dashboard')
    except Employee.DoesNotExist:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
        return redirect('employee_list')


@login_required
def employee_dashboard(request):
    """Employee's personal dashboard"""
    try:
        employee = Employee.objects.get(user=request.user)
        
        # Current month attendance
        today = datetime.now()
        today_date = today.date()
        current_month_start = today.replace(day=1)
        current_month_end = (current_month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        attendance_records = Attendance.objects.filter(
            employee=employee,
            date__range=[current_month_start, current_month_end]
        )
        
        # Attendance summary
        present_count = attendance_records.filter(status='P').count()
        absent_count = attendance_records.filter(status='A').count()
        leave_count = attendance_records.filter(status='L').count()
        
        # Today's attendance for check-in/check-out
        try:
            today_attendance = Attendance.objects.get(employee=employee, date=today_date)
            has_checked_in = today_attendance.check_in_time is not None
            has_checked_out = today_attendance.check_out_time is not None
        except Attendance.DoesNotExist:
            today_attendance = None
            has_checked_in = False
            has_checked_out = False
        
        # Today's salary slip
        today_salary_slip = None
        today_salary = 0
        try:
            today_salary_slip = DailySalarySlip.objects.get(employee=employee, date=today_date)
            today_salary = today_salary_slip.daily_salary
        except DailySalarySlip.DoesNotExist:
            pass
        
        # Monthly salary slips
        monthly_salary_slips = DailySalarySlip.objects.filter(
            employee=employee,
            date__range=[current_month_start, current_month_end]
        ).order_by('-date')
        
        # Calculate monthly accumulated salary
        from decimal import Decimal
        monthly_accumulated_salary = Decimal('0')
        for slip in monthly_salary_slips:
            monthly_accumulated_salary += slip.daily_salary
        
        # Recent payroll
        payroll_records = PayrollRecord.objects.filter(employee=employee).order_by('-payroll_month')[:3]
        
        # Pending leaves
        pending_leaves = Leave.objects.filter(employee=employee, status='P')
        
        # Get salary structure
        salary_structure = getattr(employee, 'salary_structure', None)
        
        context = {
            'employee': employee,
            'present_count': present_count,
            'absent_count': absent_count,
            'leave_count': leave_count,
            'total_attendance': attendance_records.count(),
            'payroll_records': payroll_records,
            'pending_leaves': pending_leaves,
            'today_attendance': today_attendance,
            'has_checked_in': has_checked_in,
            'has_checked_out': has_checked_out,
            'today': today_date,
            'today_salary': today_salary,
            'today_salary_slip': today_salary_slip,
            'monthly_accumulated_salary': monthly_accumulated_salary,
            'monthly_salary_slips': monthly_salary_slips,
            'salary_structure': salary_structure,
        }
        return render(request, 'gate/employee_dashboard.html', context)
    except Employee.DoesNotExist:
        return redirect('admin_dashboard')


@login_required
def employee_profile(request):
    """Display the logged-in employee's profile."""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('admin_dashboard')

    context = {
        'employee': employee,
    }
    return render(request, 'gate/employee_profile.html', context)


@login_required
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('employee_dashboard')
    
    total_employees = Employee.objects.filter(status='A').count()
    total_departments = Department.objects.count()
    
    # Today's attendance
    today = datetime.now().date()
    today_attendance = Attendance.objects.filter(date=today)
    present_today = today_attendance.filter(status='P').count()
    absent_today = today_attendance.filter(status='A').count()
    
    # Pending leaves
    pending_leaves = Leave.objects.filter(status='P').count()
    
    # Recent payrolls
    payroll_months = PayrollMonth.objects.order_by('-year', '-month')[:5]
    
    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'present_today': present_today,
        'absent_today': absent_today,
        'pending_leaves': pending_leaves,
        'payroll_months': payroll_months,
    }
    return render(request, 'gate/admin_dashboard.html', context)


# ============= EMPLOYEE MANAGEMENT =============

@login_required
def employee_list(request):
    """List all employees with filtering"""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('employee_dashboard')
    
    # Exclude hidden employees from the list
    employees = Employee.objects.select_related('department').filter(is_hidden=False)
    
    # Filter by department
    department = request.GET.get('department')
    if department:
        employees = employees.filter(department_id=department)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        employees = employees.filter(status=status)
    
    # Search
    search = request.GET.get('search')
    if search:
        employees = employees.filter(
            Q(employee_id__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    departments = Department.objects.all()
    context = {
        'employees': employees,
        'departments': departments,
    }
    return render(request, 'gate/employee_list.html', context)


@login_required
def employee_detail(request, employee_id):
    """Employee details view"""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('employee_dashboard')
    
    employee = get_object_or_404(Employee, pk=employee_id)
    salary_structure = getattr(employee, 'salary_structure', None)
    
    context = {
        'employee': employee,
        'salary_structure': salary_structure,
    }
    return render(request, 'gate/employee_detail.html', context)


@login_required
def employee_edit(request, employee_id):
    """Edit employee details"""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('employee_dashboard')
    
    employee = get_object_or_404(Employee, pk=employee_id)
    departments = Department.objects.all()
    
    if request.method == 'POST':
        try:
            from datetime import datetime as dt
            
            # Update employee fields
            employee.first_name = request.POST.get('first_name')
            employee.last_name = request.POST.get('last_name')
            employee.email = request.POST.get('email')
            employee.phone = request.POST.get('phone', '')
            
            # Parse date of birth
            dob_str = request.POST.get('date_of_birth')
            if dob_str:
                try:
                    employee.date_of_birth = dt.strptime(dob_str, '%d-%m-%Y').date()
                except ValueError:
                    try:
                        employee.date_of_birth = dt.strptime(dob_str, '%Y-%m-%d').date()
                    except ValueError:
                        employee.date_of_birth = dob_str
            
            employee.gender = request.POST.get('gender')
            
            # Employment details
            department_id = request.POST.get('department')
            if department_id:
                employee.department_id = department_id
            
            employee.designation = request.POST.get('designation')
            
            # Parse date of joining
            doj_str = request.POST.get('date_of_joining')
            if doj_str:
                try:
                    employee.date_of_joining = dt.strptime(doj_str, '%d-%m-%Y').date()
                except ValueError:
                    try:
                        employee.date_of_joining = dt.strptime(doj_str, '%Y-%m-%d').date()
                    except ValueError:
                        employee.date_of_joining = doj_str
            
            employee.status = request.POST.get('status')
            
            # Contact information
            employee.address = request.POST.get('address')
            employee.city = request.POST.get('city')
            employee.state = request.POST.get('state')
            employee.postal_code = request.POST.get('postal_code')
            
            # Bank details
            employee.bank_name = request.POST.get('bank_name', '')
            employee.account_number = request.POST.get('account_number', '')
            employee.ifsc_code = request.POST.get('ifsc_code', '')
            
            # Validate the employee
            employee.clean()
            
            # Save changes
            employee.save()
            
            from django.contrib import messages
            messages.success(request, f'Employee {employee.full_name} has been updated successfully!')
            
            return redirect('employee_detail', employee_id=employee.id)
        
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error updating employee: {str(e)}')
    
    context = {
        'employee': employee,
        'form': {},
        'departments': departments,
    }
    return render(request, 'gate/employee_edit.html', context)


@login_required
def employee_add(request):
    """Add new employee"""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('employee_dashboard')
    
    departments = Department.objects.all()
    
    if request.method == 'POST':
        try:
            from datetime import datetime as dt
            
            # Generate unique employee ID
            from django.db.models import Max
            last_employee = Employee.objects.all().order_by('-id').first()
            employee_id = f"EMP{(last_employee.id if last_employee else 0) + 1:05d}"
            
            # Parse date of birth
            dob_str = request.POST.get('date_of_birth')
            if dob_str:
                try:
                    dob = dt.strptime(dob_str, '%d-%m-%Y').date()
                except ValueError:
                    try:
                        dob = dt.strptime(dob_str, '%Y-%m-%d').date()
                    except ValueError:
                        dob = dob_str
            else:
                dob = None
            
            # Parse date of joining
            doj_str = request.POST.get('date_of_joining')
            if doj_str:
                try:
                    doj = dt.strptime(doj_str, '%d-%m-%Y').date()
                except ValueError:
                    try:
                        doj = dt.strptime(doj_str, '%Y-%m-%d').date()
                    except ValueError:
                        doj = doj_str
            else:
                doj = None
            
            # Create new employee
            employee = Employee(
                employee_id=employee_id,
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone', ''),
                date_of_birth=dob,
                gender=request.POST.get('gender'),
                department_id=request.POST.get('department'),
                designation=request.POST.get('designation'),
                date_of_joining=doj,
                status=request.POST.get('status', 'A'),
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                postal_code=request.POST.get('postal_code'),
                bank_name=request.POST.get('bank_name', ''),
                account_number=request.POST.get('account_number', ''),
                ifsc_code=request.POST.get('ifsc_code', ''),
            )
            
            # Validate the employee
            employee.clean()
            
            employee.save()
            
            from django.contrib import messages
            messages.success(request, f'Employee {employee.full_name} has been created successfully!')
            
            return redirect('employee_detail', employee_id=employee.id)
        
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f'Error creating employee: {str(e)}')
    
    context = {
        'departments': departments,
        'is_new': True,
    }
    return render(request, 'gate/employee_add.html', context)


@login_required
def employee_toggle_hidden(request, employee_id):
    """Toggle employee hidden status - hide/unhide employee"""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('employee_dashboard')
    
    employee = get_object_or_404(Employee, pk=employee_id)
    
    try:
        employee.is_hidden = not employee.is_hidden
        employee.save()
        
        from django.contrib import messages
        if employee.is_hidden:
            messages.success(request, f'Employee {employee.full_name} has been hidden from the list. Data is preserved in the database.')
        else:
            messages.success(request, f'Employee {employee.full_name} is now visible in the list.')
    except Exception as e:
        from django.contrib import messages
        messages.error(request, f'Error updating employee: {str(e)}')
    
    return redirect('employee_list')


@login_required
def employee_delete(request, employee_id):
    """Delete employee"""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('employee_dashboard')
    
    employee = get_object_or_404(Employee, pk=employee_id)
    
    try:
        employee_name = employee.full_name
        employee.delete()
        
        from django.contrib import messages
        messages.success(request, f'Employee {employee_name} has been deleted successfully!')
    except Exception as e:
        from django.contrib import messages
        messages.error(request, f'Error deleting employee: {str(e)}')
    
    return redirect('employee_list')


@login_required
def attendance_report(request):
    """View attendance report for a range"""
    if not (request.user.is_staff or request.user.is_superuser):
        try:
            employee = Employee.objects.get(user=request.user)
            return attendance_report_employee(request, employee.id)
        except Employee.DoesNotExist:
            return redirect('employee_dashboard')
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    employee_filter = request.GET.get('employee')
    
    attendance_records = Attendance.objects.select_related('employee').all()
    
    if start_date:
        attendance_records = attendance_records.filter(date__gte=start_date)
    if end_date:
        attendance_records = attendance_records.filter(date__lte=end_date)
    if employee_filter:
        attendance_records = attendance_records.filter(employee_id=employee_filter)
    
    attendance_records = attendance_records.order_by('-date')
    
    # Group attendance records by date
    grouped_by_date = {}
    for record in attendance_records:
        if record.date not in grouped_by_date:
            grouped_by_date[record.date] = []
        grouped_by_date[record.date].append(record)
    
    employees = Employee.objects.filter(status='A')
    
    context = {
        'grouped_by_date': grouped_by_date,
        'employees': employees,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'gate/attendance_report.html', context)


# ============= LEAVE MANAGEMENT =============

@login_required
def leave_request(request):
    """Create new leave request"""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('login')
    
    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        certificate = request.FILES.get('certificate', None)
        
        leave = Leave.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status='P'
        )
        
        if certificate:
            leave.certificate = certificate
            leave.save()
        
        return redirect('leave_list')
    
    # Filter leave types based on employee gender
    all_leave_types = Leave._meta.get_field('leave_type').choices
    leave_types = []
    
    for value, label in all_leave_types:
        # CL and UL are available for all
        if value in ['CL', 'UL']:
            leave_types.append((value, label))
        # ML only for female
        elif value == 'ML' and employee.gender == 'F':
            leave_types.append((value, label))
        # PL only for male
        elif value == 'PL' and employee.gender == 'M':
            leave_types.append((value, label))
    
    context = {
        'leave_types': leave_types,
        'employee': employee,
    }
    return render(request, 'gate/leave_request.html', context)


@login_required
def leave_list(request):
    """View leaves"""
    try:
        employee = Employee.objects.get(user=request.user)
        leaves = employee.leaves.all().order_by('-start_date')
    except Employee.DoesNotExist:
        if not (request.user.is_staff or request.user.is_superuser):
            return redirect('login')
        leaves = Leave.objects.all().order_by('-start_date')
    
    context = {
        'leaves': leaves,
    }
    return render(request, 'gate/leave_list.html', context)


@login_required
def leave_approve(request, leave_id):
    """Approve or reject leave"""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('leave_list')
    
    leave = get_object_or_404(Leave, pk=leave_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            leave.status = 'A'
        elif action == 'reject':
            leave.status = 'R'
        
        leave.approved_by = request.user
        leave.approval_date = datetime.now()
        leave.save()
        
        return redirect('leave_list')
    
    context = {
        'leave': leave,
    }
    return render(request, 'gate/leave_approve.html', context)


# ============= SALARY & PAYROLL =============

@login_required
def salary_structure(request):
    """View/Edit salary structure"""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('employee_dashboard')
    
    employee_id = request.GET.get('employee_id')

    #employee select panna list show pannum
    if not employee_id:
        employees = Employee.objects.filter(status='A').order_by('first_name')
        return render(request, 'gate/employee_list.html', {'employees': employees})
    
    employee = get_object_or_404(Employee, pk=employee_id)
    
    try:
        salary = employee.salary_structure
    except SalaryStructure.DoesNotExist:
        salary = None
    
    if request.method == 'POST':
        SalaryStructure.objects.update_or_create(
            employee=employee,
            defaults={
                'basic_salary': request.POST.get('basic_salary'),
                'hra': request.POST.get('hra', 0),
                'dearness_allowance': request.POST.get('dearness_allowance', 0),
                'conveyance': request.POST.get('conveyance', 0),
                'medical_allowance': request.POST.get('medical_allowance', 0),
                'other_allowances': request.POST.get('other_allowances', 0),
                'pf_contribution': request.POST.get('pf_contribution', 0),
                'esi_contribution': request.POST.get('esi_contribution', 0),
                'income_tax': request.POST.get('income_tax', 0),
                'other_deductions': request.POST.get('other_deductions', 0),
            }
        )
        # Apply income tax logic: 0 if annual gross <= 12,00,000
        salary = SalaryStructure.objects.get(employee=employee)
        annual_gross = salary.gross_salary * 12
        if annual_gross <= 1200000:
            salary.income_tax = 0
            salary.save()
        return redirect(f'/salary-structure/?employee_id={employee_id}')
    
    context = {
        'employee': employee,
        'salary': salary,
    }
    return render(request, 'gate/salary_structure.html', context)


@login_required
def payroll_processing(request):
    """Process payroll for a month"""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('employee_dashboard')
    
    if request.method == 'POST':
        month = request.POST.get('month')
        year = request.POST.get('year')
        
        # Convert to proper types
        month_str = str(month).zfill(2)
        year_int = int(year)
        
        # Create or get payroll month
        payroll_month, created = PayrollMonth.objects.get_or_create(
            month=f"{year_int}-{month_str}",
            year=year_int,
            defaults={'status': 'DRAFT'}
        )
        
        # Process payroll for all employees
        employees = Employee.objects.filter(status='A')
        
        # Calculate working days for the month (all days except Sundays and company holidays)
        from calendar import monthrange
        from datetime import date, timedelta
        month_start = date(year_int, int(month), 1)
        if int(month) == 12:
            month_end = date(year_int + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year_int, int(month) + 1, 1) - timedelta(days=1)
        
        # List all days in the month
        total_days = (month_end - month_start).days + 1
        all_dates = [month_start + timedelta(days=i) for i in range(total_days)]
        
        # Get all company holidays in this month
        holidays = set(HolidayCalendar.objects.filter(date__range=[month_start, month_end]).values_list('date', flat=True))
        
        # Working days: all days except Sundays and holidays
        working_days = sum(1 for d in all_dates if d.weekday() != 6 and d not in holidays)
        
        for employee in employees:
            try:
                salary_structure = employee.salary_structure
            except SalaryStructure.DoesNotExist:
                continue
            
            # Get attendance data
            attendance_records = Attendance.objects.filter(
                employee=employee,
                date__range=[month_start, month_end]
            )
            
            present_days = attendance_records.filter(status='P').count()
            absent_days = attendance_records.filter(status='A').count()
            leave_days = attendance_records.filter(status__in=['L', 'ML', 'PL']).count()
            
            payroll_record, created = PayrollRecord.objects.update_or_create(
                employee=employee,
                payroll_month=payroll_month,
                defaults={
                    'working_days': working_days,
                    'present_days': present_days,
                    'absent_days': absent_days,
                    'leave_days': leave_days,
                    'basic_salary': salary_structure.basic_salary,
                    'hra': salary_structure.hra,
                    'dearness_allowance': salary_structure.dearness_allowance,
                    'conveyance': salary_structure.conveyance,
                    'medical_allowance': salary_structure.medical_allowance,
                    'other_allowances': salary_structure.other_allowances,
                    'pf_contribution': salary_structure.pf_contribution,
                    'esi_contribution': salary_structure.esi_contribution,
                    'income_tax': salary_structure.income_tax,
                    'other_deductions': salary_structure.other_deductions,
                }
            )
            
            payroll_record.calculate_salary()
            payroll_record.save()
            
            # Create salary slip
            slip_number = f"SLIP-{payroll_month.month}-{employee.employee_id}"
            SalarySlip.objects.get_or_create(
                payroll_record=payroll_record,
                defaults={'slip_number': slip_number}
            )
        
        payroll_month.status = 'PROCESSED'
        payroll_month.processing_date = datetime.now()
        payroll_month.processed_by = request.user
        payroll_month.save()
        
        return redirect('payroll_records')
    
    context = {
        'months': range(1, 13),
        'current_year': datetime.now().year,
    }
    return render(request, 'gate/payroll_processing.html', context)


@login_required
def payroll_records(request):
    """View payroll records"""
    if not (request.user.is_staff or request.user.is_superuser):
        try:
            employee = Employee.objects.get(user=request.user)
            payroll_records = employee.payroll_records.all().order_by('-payroll_month')
        except Employee.DoesNotExist:
            return redirect('login')
    else:
        payroll_month = request.GET.get('payroll_month')
        payroll_records = PayrollRecord.objects.select_related('payroll_month').all()
        
        if payroll_month:
            payroll_records = payroll_records.filter(payroll_month_id=payroll_month)
        
        payroll_records = payroll_records.order_by('-payroll_month')
    
    payroll_months = PayrollMonth.objects.all().order_by('-year', '-month')
    
    context = {
        'payroll_records': payroll_records,
        'payroll_months': payroll_months,
    }
    return render(request, 'gate/payroll_records.html', context)


@login_required
def salary_slip_view(request, slip_id):
    """View salary slip"""
    salary_slip = get_object_or_404(SalarySlip, pk=slip_id)
    payroll_record = salary_slip.payroll_record
    employee = payroll_record.employee
    
    # Check if user has permission to view
    try:
        user_employee = Employee.objects.get(user=request.user)
        if user_employee.id != employee.id and not request.user.is_staff:
            return redirect('leave_list')
    except Employee.DoesNotExist:
        if not request.user.is_staff:
            return redirect('login')
    
    # Calculate attendance-based salary
    import calendar
    year, month = map(int, payroll_record.payroll_month.month.split('-'))
    total_days_in_month = calendar.monthrange(year, month)[1]
    
    per_day_salary = payroll_record.net_salary / total_days_in_month
    final_payable_salary = payroll_record.final_payable_salary  # Use the property
    
    # Round to 2 decimal places
    per_day_salary = round(per_day_salary, 2)
    
    context = {
        'salary_slip': salary_slip,
        'payroll_record': payroll_record,
        'employee': employee,
        'total_days_in_month': total_days_in_month,
        'per_day_salary': per_day_salary,
        'final_payable_salary': final_payable_salary,
    }
    return render(request, 'gate/salary_slip.html', context)


@login_required
def employee_salary_structure(request):
    """View employee's own salary structure"""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('login')
    
    salary_structure = getattr(employee, 'salary_structure', None)
    
    if not salary_structure:
        from django.contrib import messages
        messages.info(request, 'Your salary structure has not been created yet. Please contact the admin.')
    
    context = {
        'employee': employee,
        'salary_structure': salary_structure,
    }
    return render(request, 'gate/employee_salary_structure.html', context)


@login_required
def employee_daily_salary_slips(request):
    """View employee's daily salary slips"""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('login')
    
    # Get month and year from query params or use current month
    from django.utils import timezone
    today = timezone.now()
    
    year = request.GET.get('year', today.year)
    month = request.GET.get('month', today.month)
    
    try:
        year = int(year)
        month = int(month)
    except (ValueError, TypeError):
        year = today.year
        month = today.month
    
    # Calculate month boundaries
    month_start = datetime(year, month, 1).date()
    if month == 12:
        month_end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        month_end = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    # Get daily salary slips for the month
    daily_salary_slips = DailySalarySlip.objects.filter(
        employee=employee,
        date__range=[month_start, month_end]
    ).order_by('-date')
    
    # Calculate total salary for the month
    from decimal import Decimal
    total_monthly_salary = Decimal('0')
    for slip in daily_salary_slips:
        total_monthly_salary += slip.daily_salary
    
    # Get salary structure for reference
    salary_structure = getattr(employee, 'salary_structure', None)
    
    # Calculate daily salary
    daily_salary = Decimal('0')
    if salary_structure:
        daily_salary = salary_structure.gross_salary / Decimal('30')
    
    context = {
        'employee': employee,
        'daily_salary_slips': daily_salary_slips,
        'total_monthly_salary': total_monthly_salary,
        'salary_structure': salary_structure,
        'daily_salary': daily_salary,
        'month': month,
        'year': year,
        'month_name': calendar.month_name[month],
    }
    return render(request, 'gate/employee_daily_salary_slips.html', context)


# ============= MOBILE CHECK-IN / CHECK-OUT SYSTEM =============

@login_required
def mobile_checkin_dashboard(request):
    """Mobile-friendly dashboard for check-in/check-out"""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('login')
    
    from django.utils import timezone
    today = timezone.now().date()
    
    # Get today's attendance record if exists
    try:
        today_attendance = Attendance.objects.get(employee=employee, date=today)
        has_checked_in = today_attendance.check_in_time is not None
        has_checked_out = today_attendance.check_out_time is not None
    except Attendance.DoesNotExist:
        today_attendance = None
        has_checked_in = False
        has_checked_out = False
    
    context = {
        'employee': employee,
        'today_attendance': today_attendance,
        'has_checked_in': has_checked_in,
        'has_checked_out': has_checked_out,
        'today': today,
    }
    return render(request, 'gate/mobile_checkin.html', context)


@login_required
@require_http_methods(["POST"])
def employee_checkin(request):
    """Handle employee check-in"""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Employee not found'}, status=404)
    
    from django.utils import timezone
    from decimal import Decimal
    now = timezone.now()
    today = now.date()
    current_time = now.time()
    
    try:
        # Check if attendance record already exists for today
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={
                'status': 'P',
                'check_in_time': current_time,
            }
        )
        
        # If record already existed, update only if no check-in time yet
        if not created:
            if attendance.check_in_time is None:
                attendance.check_in_time = current_time
                attendance.status = 'P'
                attendance.save()
            else:
                return JsonResponse({
                    'status': 'warning',
                    'message': f'Already checked in at {attendance.check_in_time.strftime("%H:%M:%S")}',
                    'check_in_time': attendance.check_in_time.strftime("%H:%M:%S"),
                })
        
        # Create or update DailySalarySlip
        try:
            salary_structure = employee.salary_structure
            # Calculate daily salary as gross_salary / 30
            daily_salary = salary_structure.gross_salary / Decimal('30')
            
            # Create or update DailySalarySlip
            daily_slip, slip_created = DailySalarySlip.objects.get_or_create(
                employee=employee,
                date=today,
                defaults={
                    'attendance': attendance,
                    'daily_salary': daily_salary,
                }
            )
            
            # If already existed, update the salary slip
            if not slip_created:
                daily_slip.daily_salary = daily_salary
                daily_slip.attendance = attendance
                daily_slip.save()
        
        except SalaryStructure.DoesNotExist:
            # Salary structure not defined for this employee - log but continue
            pass
        
        return JsonResponse({
            'status': 'success',
            'message': f'Checked in at {current_time.strftime("%H:%M:%S")}',
            'check_in_time': current_time.strftime("%H:%M:%S"),
        })
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def employee_checkout(request):
    """Handle employee check-out"""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Employee not found'}, status=404)
    
    from django.utils import timezone
    now = timezone.now()
    today = now.date()
    current_time = now.time()
    
    try:
        # Get today's attendance record
        try:
            attendance = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            # If no attendance record exists, create one with check-out only
            attendance = Attendance.objects.create(
                employee=employee,
                date=today,
                status='P',
                check_out_time=current_time,
            )
            return JsonResponse({
                'status': 'warning',
                'message': f'No check-in found. Checked out at {current_time.strftime("%H:%M:%S")}',
                'check_out_time': current_time.strftime("%H:%M:%S"),
            })
        
        # Check if already checked out
        if attendance.check_out_time is not None:
            return JsonResponse({
                'status': 'warning',
                'message': f'Already checked out at {attendance.check_out_time.strftime("%H:%M:%S")}',
                'check_out_time': attendance.check_out_time.strftime("%H:%M:%S"),
            })
        
        # Update check-out time
        attendance.check_out_time = current_time
        attendance.save()
        
        # Calculate working hours
        if attendance.check_in_time:
            from datetime import datetime, time
            check_in_dt = datetime.combine(today, attendance.check_in_time)
            check_out_dt = datetime.combine(today, current_time)
            working_hours = (check_out_dt - check_in_dt).total_seconds() / 3600
            working_hours_str = f"{int(working_hours)}h {int((working_hours % 1) * 60)}m"
        else:
            working_hours_str = "N/A"
        
        return JsonResponse({
            'status': 'success',
            'message': f'Checked out at {current_time.strftime("%H:%M:%S")}',
            'check_out_time': current_time.strftime("%H:%M:%S"),
            'working_hours': working_hours_str,
        })
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ============= UTILITY FUNCTIONS =============

@login_required
def attendance_calendar(request, year=None, month=None):
    """Display attendance calendar"""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('employee_dashboard')
    
    today = datetime.now()
    if not year:
        year = today.year
    if not month:
        month = today.month
    
    # Get attendance for the month
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    attendance_records = Attendance.objects.filter(
        employee=employee,
        date__range=[start_date, end_date]
    ).values('date', 'status')
    
    attendance_dict = {rec['date']: rec['status'] for rec in attendance_records}
    
    # Build calendar
    cal = monthcalendar(year, month)
    calendar_data = []
    
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)
            else:
                date_obj = datetime(year, month, day).date()
                status = attendance_dict.get(date_obj, None)
                week_data.append({
                    'day': day,
                    'status': status,
                    'date': date_obj,
                })
        calendar_data.append(week_data)
    
    context = {
        'employee': employee,
        'year': year,
        'month': month,
        'month_name': month_name[month],
        'calendar': calendar_data,
        'status_choices': Attendance._meta.get_field('status').choices,
    }
    return render(request, 'gate/attendance_calendar.html', context)
