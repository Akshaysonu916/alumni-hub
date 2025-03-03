from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import AlumniProfile, StudentProfile, JobPost, Event

# 1. User Registration Form (Common for Students & Alumni)
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# 2. Alumni Profile Update Form
# class AlumniProfileForm(forms.ModelForm):
#     class Meta:
#         model = AlumniProfile
#         fields = ['full_name', 'current_company', 'contact_number', 'linkedin_profile', 'bio']

# 3. Student Profile Update Form
# class StudentProfileForm(forms.ModelForm):
#     class Meta:
#         model = StudentProfile
#         fields = ['full_name', 'degree', 'academic_year', 'interests', 'contact_number']

# 4. Job Posting Form (For Alumni)
# class JobPostForm(forms.ModelForm):
#     class Meta:
#         model = JobPost
#         fields = ['title', 'company', 'location', 'job_type', 'description', 'application_link']

# 5. Event Creation Form (For Admin)
# class EventForm(forms.ModelForm):
#     class Meta:
#         model = Event
#         fields = ['title', 'description', 'date', 'location']
