# Generated by Django 5.1.6 on 2025-04-07 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0024_alumniprofile_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='alumniprofile',
            name='department',
            field=models.CharField(default=4, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='alumniprofile',
            name='passout_year',
            field=models.IntegerField(default=2),
            preserve_default=False,
        ),
    ]
