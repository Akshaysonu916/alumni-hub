# Generated by Django 5.1.6 on 2025-04-01 10:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0019_photo_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobpost',
            name='application_link',
        ),
    ]
