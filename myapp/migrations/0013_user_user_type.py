# Generated by Django 5.1.6 on 2025-03-24 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0012_delete_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('admin', 'Admin'), ('alumni', 'Alumni'), ('student', 'Student')], default='student', max_length=10),
        ),
    ]
