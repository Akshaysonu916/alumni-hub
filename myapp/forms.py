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
#         fields = '__all__'
#         widgets = {
#             'job_name': forms.TextInput(attrs={
#                 'class': 'form-control block w-full px-4 py-2 m-3 text-gray-900 bg-gray-50 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500',
#                 'placeholder': 'Enter product name',
#             }),
#             'company': forms.TextInput(attrs={
#                 'class': 'form-control block w-full px-4 py-2 m-3 text-gray-900 bg-gray-50 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500',
#                 'placeholder': 'Enter company name',
#             }),
#             'description': forms.Textarea(attrs={
#                 'class': 'form-control block w-full px-4 py-2 m-3 text-gray-900 bg-gray-50 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500',
#                 'placeholder': 'Enter description',
#                 'rows': 4,
#             }),
#             'job_type': forms.TextInput(attrs={
#                 'class': 'form-control block w-full px-4 py-2 m-3 text-gray-900 bg-gray-50 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500',
#                 'placeholder': 'Enter job_type',
#             }),
#             'application_link': forms.URLInput(attrs={
#                 'class': 'form-control block w-full px-4 py-2 m-3 text-gray-900 bg-gray-50 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500',
#             }),
#         }

class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = ['job_name', 'company', 'description', 'job_type', 'application_link']
        widgets = {
            'job_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Job Title'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Job Description'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'application_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Application Link'}),
        }


# 5. Event Creation Form (For Admin)
# class EventForm(forms.ModelForm):
#     class Meta:
#         model = Event
#         fields = ['title', 'description', 'date', 'location']
