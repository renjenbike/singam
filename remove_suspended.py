#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garments.settings')
django.setup()

from gate.models import Employee

# Delete employees with Suspended status
count = Employee.objects.filter(status='S').delete()
print(f"Deleted {count[0]} employees with Suspended status")
