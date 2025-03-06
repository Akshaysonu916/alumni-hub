from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

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


class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = ['job_name', 'company', 'description', 'job_type', 'application_link','company_website']
        widgets = {
            'job_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Job Title'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Job Description'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'application_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Application Link'}),
            'company_website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Company Website Link'}),
        }

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'description', 'image']  # Fields to include in the form
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter a description'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

# 5. Event Creation Form (For Admin)
# class EventForm(forms.ModelForm):
#     class Meta:
#         model = Event
#         fields = ['title', 'description', 'date', 'location']
