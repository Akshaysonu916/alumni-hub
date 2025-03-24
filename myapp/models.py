from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    USER_TYPES = [
        ('alumni', 'Alumni'),
        ('student', 'Student'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='student')



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

class JobPost(models.Model):
    job_name = models.CharField(max_length=100,default="Unnamed Job")
    company = models.CharField(max_length=255)
    description = models.TextField(blank=True)  # Changed to TextField
    job_type = models.CharField(
        max_length=100,
        choices=[("FT", "Full-Time"), ("PT", "Part-Time"),("IS", "Intern-Ship"),("RT", "Remote-Job")],
        default=4  # Added default value
    )
    application_link = models.URLField(blank=True, null=True)  # Allowing blank values
    company_website = models.URLField(blank=True, null=True)  # New field for company site link

    def __str__(self):
        return self.job_name
    

class Photo(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)  # Optional title for the photo
    description = models.TextField(blank=True, null=True)  # Optional description
    image=models.ImageField(upload_to='images') # Image field, uploads to 'photos/' directory
    upload_date = models.DateTimeField(default=timezone.now)  # Automatically set to the current date and time

    def __str__(self):
        return self.title or f"Photo {self.id}"  # Return the title or a default string

# Chat Model (Between Alumni & Students)
# class ChatMessage(models.Model):
#     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
#     receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
#     message = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Message from {self.sender.username} to {self.receiver.username}"

