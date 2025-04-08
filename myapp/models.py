from django.contrib.auth.models import AbstractUser,Group,Permission
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    is_alumni = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)



# Alumni Profile Model
class AlumniProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='alumni_profile')
    company = models.CharField(max_length=255, blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    graduation_year = models.PositiveIntegerField(default=2025)
    linkedin = models.URLField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    department = models.CharField(max_length=100)  # <- Make sure this exists
    passout_year = models.IntegerField()           # <- And this too


    def __str__(self):
        return f"{self.user.username} - {self.job_title} at {self.company}"

# Student Profile Model
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    enrollment_year = models.PositiveIntegerField()
    major = models.CharField(max_length=255)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
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
    company_website = models.URLField(blank=True, null=True)  # New field for company site link
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_posts')

    def __str__(self):
        return self.job_name
    

class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Track who uploaded the photo
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='images')
    upload_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title or f"Photo {self.id}"# Return the title or a default string

# Chat Model (Between Alumni & Students)
# class ChatMessage(models.Model):
#     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
#     receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
#     message = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Message from {self.sender.username} to {self.receiver.username}"

