from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('employee-dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('my-profile/', views.employee_profile, name='employee_profile'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Employee Management
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_add, name='employee_add'),
    path('employees/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:employee_id>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:employee_id>/toggle-hidden/', views.employee_toggle_hidden, name='employee_toggle_hidden'),
    path('employees/<int:employee_id>/delete/', views.employee_delete, name='employee_delete'),
    
    # Attendance
    path('attendance/report/', views.attendance_report, name='attendance_report'),
    path('attendance/calendar/<int:year>/<int:month>/', views.attendance_calendar, name='attendance_calendar'),
    path('attendance/calendar/', views.attendance_calendar, name='attendance_calendar_current'),
    
    # Mobile Check-In / Check-Out
    path('mobile-checkin/', views.mobile_checkin_dashboard, name='mobile_checkin_dashboard'),
    path('mobile-checkin/checkin/', views.employee_checkin, name='employee_checkin'),
    path('mobile-checkin/checkout/', views.employee_checkout, name='employee_checkout'),
    
    # Leave Management
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/request/', views.leave_request, name='leave_request'),
    path('leaves/<int:leave_id>/approve/', views.leave_approve, name='leave_approve'),
    
    # Salary & Payroll
    path('salary-structure/', views.salary_structure, name='salary_structure'),
    path('my-salary-structure/', views.employee_salary_structure, name='employee_salary_structure'),
    path('my-salary-slips/', views.employee_daily_salary_slips, name='employee_daily_salary_slips'),
    path('payroll/process/', views.payroll_processing, name='payroll_processing'),
    path('payroll/records/', views.payroll_records, name='payroll_records'),
    path('payroll/salary-slip/<int:slip_id>/', views.salary_slip_view, name='salary_slip_view'),
]
