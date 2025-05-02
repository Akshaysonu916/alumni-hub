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
    passout_year = models.IntegerField(default=2025)           # <- And this too


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
    job_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    description = models.TextField()
    job_type = models.CharField(max_length=20, choices=(
        ('FT', 'Full-Time'),
        ('PT', 'Part-Time'),
        ('IS', 'Internship'),
        ('RT', 'Remote-Job'),
    ))
    company_website = models.URLField(blank=True, null=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_posts')  # ✅ Important

    def _str_(self):
        return self.job_name
    

class Notification(models.Model):
    TYPE_CHOICES = [
        ('job', 'Job Post'),
        ('connection', 'Connection Request'),
        ('connection_accepted', 'Connection Accepted'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')  # recipient
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')  # sender
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='job')



    def _str_(self):
        return f"Notification for {self.notification_type} - {self.message}"
 
class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Track who uploaded the photo
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='images')
    upload_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title or f"Photo {self.id}"# Return the title or a default string
    

class Connection(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')  # Prevent duplicate requests

    def _str_(self):
        return f"{self.from_user} → {self.to_user} ({'Accepted' if self.is_accepted else 'Pending'})"

# Chat Model (Between Alumni & Students)
# class ChatMessage(models.Model):
#     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
#     receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
#     message = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Message from {self.sender.username} to {self.receiver.username}"

