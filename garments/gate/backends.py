from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import Employee


class EmployeeIdBackend(ModelBackend):
    """
    Custom authentication backend that allows login using Employee ID.
    Username field accepts employee_id and password should match employee_id as well.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find employee by employee_id
            employee = Employee.objects.get(employee_id=username)
            
            # Check if password matches employee_id
            if password == employee.employee_id:
                # Get or create associated user
                user = employee.user
                if user is None:
                    # Create a user if it doesn't exist
                    user = User.objects.create_user(
                        username=employee.employee_id,
                        email=employee.email,
                        first_name=employee.first_name,
                        last_name=employee.last_name
                    )
                    employee.user = user
                    employee.save()
                
                return user
            else:
                return None
        except Employee.DoesNotExist:
            # Try default authentication as fallback (for admin)
            return super().authenticate(request, username=username, password=password, **kwargs)
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
