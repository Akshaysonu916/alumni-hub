from django.contrib.auth.models import AbstractUser
from django.db import models

# Custom User Model with Role-based access
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",  # Unique related_name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",  # Unique related_name
        blank=True
    )

# Alumni Profile Model
class AlumniProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='alumni_profile')
    company = models.CharField(max_length=255, blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    graduation_year = models.PositiveIntegerField()
    linkedin = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.job_title} at {self.company}"

# Student Profile Model
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    enrollment_year = models.PositiveIntegerField()
    major = models.CharField(max_length=255)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.major}"

# Job Post Model (Posted by Alumni)
class JobPost(models.Model):
    alumni = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_posts', limit_choices_to={'role': 'alumni'})
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    job_description = models.TextField()
    apply_link = models.URLField()
    posted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company_name} by {self.alumni.username}"

# Events Model (Managed by Admin)
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events', limit_choices_to={'role': 'admin'})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Chat Model (Between Alumni & Students)
class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

