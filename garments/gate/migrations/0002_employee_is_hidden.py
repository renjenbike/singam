# Generated migration for adding is_hidden field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gate', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='is_hidden',
            field=models.BooleanField(default=False, help_text='Hide employee from regular list but keep data in database'),
        ),
    ]
