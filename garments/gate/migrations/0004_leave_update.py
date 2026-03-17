# Generated migration for updating Leave model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gate', '0002_employee_is_hidden'),
    ]

    operations = [
        migrations.AddField(
            model_name='leave',
            name='certificate',
            field=models.FileField(blank=True, help_text='Upload certificate for Maternity/Paternity leave', null=True, upload_to='leave_certificates/'),
        ),
        migrations.AlterField(
            model_name='leave',
            name='leave_type',
            field=models.CharField(
                choices=[('CL', 'Casual Leave'), ('UL', 'Unpaid Leave'), ('ML', 'Maternity Leave'), ('PL', 'Paternity Leave')],
                max_length=2
            ),
        ),
    ]
