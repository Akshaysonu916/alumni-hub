from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

# 1. User Registration Form (Common for Students & Alumni)
class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)
    user_type = forms.ChoiceField(
        choices=[("student", "Student"), ("alumni", "Alumni")],
        required=True,
        label="Register as"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'user_type')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_student = self.cleaned_data["user_type"] == "student"
        user.is_alumni = self.cleaned_data["user_type"] == "alumni"

        if commit:
            user.save()
        
        return user
    
class SignInForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

# class AlumniProfileForm(forms.ModelForm):
#     class Meta:
#         model = AlumniProfile
#         fields = ['company', 'job_title', 'graduation_year', 'linkedin']
#         widgets = {
#             'company': forms.TextInput(attrs={'class': 'border border-black'}),
#             'job_title': forms.TextInput(attrs={'class': 'border border-black'}),
#             'graduation_year': forms.NumberInput(attrs={'class': 'border border-black'}),
#             'linkedin': forms.URLInput(attrs={'class': 'border border-black'}),
#         }

# # 3. Student Profile Update Form
# class StudentProfileForm(forms.ModelForm):
#     class Meta:
#         model = StudentProfile
#         fields = ['full_name', 'degree', 'academic_year', 'interests', 'contact_number']


class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = ['job_name', 'company', 'description', 'job_type','company_website']
        widgets = {
            'job_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Job Title'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Job Description'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
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
class AlumniProfileForm(forms.ModelForm):
    class Meta:
        model = AlumniProfile
        fields = ["company", "job_title", "graduation_year", "linkedin","profile_picture"]

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ["enrollment_year", "major", "resume",'profile_picture']