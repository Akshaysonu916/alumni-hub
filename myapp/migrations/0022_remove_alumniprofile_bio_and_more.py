# Generated by Django 5.1.6 on 2025-04-01 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0021_alumniprofile_bio_alumniprofile_profile_picture_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alumniprofile',
            name='bio',
        ),
        migrations.RemoveField(
            model_name='alumniprofile',
            name='profile_picture',
        ),
        migrations.AlterField(
            model_name='alumniprofile',
            name='company',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='alumniprofile',
            name='graduation_year',
            field=models.PositiveIntegerField(default=2025),
        ),
        migrations.AlterField(
            model_name='alumniprofile',
            name='job_title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='enrollment_year',
            field=models.PositiveIntegerField(),
        ),
    ]
