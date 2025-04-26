from django.shortcuts import render,redirect,get_object_or_404
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required ,user_passes_test
from django.contrib import messages
from django.contrib.auth import logout,login,authenticate,get_user_model
from django.http import HttpResponseForbidden
from django.db.models import Q
from django.http import JsonResponse


# Create your views here.

def is_alumni(user):
    return user.is_authenticated and user.profile.user_type == 'alumni'

@user_passes_test(is_alumni)
@login_required(login_url='signin')
def add_job(request):
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            return redirect('jobpost_list')  # Change this to your actual job listing view name
    else:
        form = JobPostForm()
    return render(request, 'addjobs.html', {'form': form})


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('signin')  # Redirect to login page after signup
        else:
            print(form.errors)  # Debugging: Print form errors in terminal
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect, render

def signin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Check if admin (either superuser or staff)
            if user.is_superuser or user.is_staff:
                return redirect('admin_dashboard')  # or use reverse('admin:index')
            
            # Check user type from profile or directly from user model
            elif hasattr(user, 'profile') and user.profile.user_type in ['alumni', 'student']:
                return redirect('home')

            # Fallback redirect
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('signin')

    return render(request, 'signin.html')


def home_view(request):
    return render(request,'home.html',{'user':request.user})


def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully signout.")
    return redirect('signin')



#job posts all operations
@login_required(login_url='signin')
def jobpost_list(request):
    query = request.GET.get("q")  # Get the search query from URL if it exists

    if query:
        jobs = JobPost.objects.filter(
            Q(job_name__icontains=query) 
        )
    else:
        jobs = JobPost.objects.all()  # No search, return all jobs

    return render(request, 'jobpost_list.html', {'jobs': jobs})

def userjobs_view(request):
    jobs = JobPost.objects.all()
    return render(request, 'userjobs.html', {'jobs': jobs})

def job_post_detail(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)
    return render(request, 'jobpost_detail.html', {'job': job})


@login_required
def edit_jobpost(request, job_id):
    jobpost = get_object_or_404(JobPost, id=job_id)

    # ✅ Permission check
    if request.user != jobpost.posted_by and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to edit this job post.")

    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=jobpost)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job post updated successfully.')
            return redirect('jobpost_detail', job_id=jobpost.id)
    else:
        form = JobPostForm(instance=jobpost)

    return render(request, 'edit_jobpost.html', {'form': form, 'jobpost': jobpost})


def delete_jobpost(request, job_id):
    jobpost = get_object_or_404(JobPost, id=job_id)
    if request.method == 'POST':
        jobpost.delete()
        messages.success(request, 'Job post deleted successfully.')
        return redirect('jobpost_list')
    return render(request, 'confirm_delete.html', {'jobpost': jobpost})

# photos sections
# View to display the photo gallery
@login_required(login_url='signin')
def photo_gallery(request):
    photos = Photo.objects.all().order_by('-upload_date')  # Fetch all photos, ordered by upload date
    return render(request, 'photo_gallery.html', {'photos': photos})

# View to handle photo uploads
def upload_photo(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)  # Don't save to DB yet
            photo.user = request.user         # Assign logged-in user
            photo.save()                      # Now save to DB
            messages.success(request, "Photo uploaded successfully!")
            return redirect('photo_gallery')
    else:
        form = PhotoForm()
    
    return render(request, 'upload_photo.html', {'form': form})



def photo_detail(request, id):
    photo = get_object_or_404(Photo, id=id)
    return render(request, 'photo_detail.html', {'photo': photo})

# Edit Photo View
@login_required
def edit_photo(request, id):
    photo = get_object_or_404(Photo, id=id)
    
    # Check authorization
    if request.user != photo.user and not request.user.is_superuser:
        messages.error(request, "You are not authorized to edit this photo.")
        return redirect('photo_detail', id=photo.id)

    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, "Photo updated successfully!")
            return redirect('photo_detail', id=photo.id)
    else:
        form = PhotoForm(instance=photo)

    return render(request, 'edit_photo.html', {'form': form, 'photo': photo})


@login_required
def delete_photo(request, id):
    photo = get_object_or_404(Photo, id=id)

    # Check authorization
    if request.user != photo.user and not request.user.is_superuser:
        messages.error(request, "You are not authorized to delete this photo.")
        return redirect('photo_detail', id=photo.id)

    if request.method == 'POST':
        photo.delete()
        messages.success(request, "Photo deleted successfully!")
        return redirect('photo_gallery')

    return render(request, 'delete_photo.html', {'photo': photo})


@login_required
def profile_view(request):
    """Display the profile of the logged-in user based on their role."""
    try:
        if hasattr(request.user, 'alumni_profile'):
            profile = request.user.alumni_profile
            template = "alumni_profile.html"
        elif hasattr(request.user, 'student_profile'):
            profile = request.user.student_profile
            template = "student_profile.html"
        else:
            return redirect("edit_profile")  # Redirect to profile edit if no profile exists

        return render(request, template, {"profile": profile})

    except Exception as e:
        print(f"Error loading profile: {e}")
        return redirect("edit_profile")  # Handle missing profiles gracefully


@login_required
def edit_profile_view(request):
    user = request.user

    if hasattr(user, 'is_alumni') and user.is_alumni:
        profile, created = AlumniProfile.objects.get_or_create(user=user)
        form_class = AlumniProfileForm
    elif hasattr(user, 'is_student') and user.is_student:
        # Provide defaults for required fields
        profile, created = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'enrollment_year': 2020,  # 👈 You can customize this
                # 'graduation_year': 2024,  # 👈 Or calculate from current year
            }
        )
        form_class = StudentProfileForm
    else:
        return HttpResponseForbidden("Invalid user type or missing profile.")

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = form_class(instance=profile)

    return render(request, "edit_profile.html", {"form": form})




def is_admin(user):
    return user.is_staff



@user_passes_test(is_admin)
def admin_dashboard(request):
    alumni = AlumniProfile.objects.all()
    students = StudentProfile.objects.all()
    jobs = JobPost.objects.all()
    gallery = Photo.objects.all()

    context = {
        'alumni': alumni,
        'students': students,
        'jobs': jobs,
        'gallery': gallery,
    }
    return render(request, 'admin_dashboard.html', context)

@user_passes_test(is_admin)
@login_required(login_url='signin')
def admin_alumni_list(request):
    alumni = AlumniProfile.objects.all()
    return render(request, 'alumni_list.html', {'alumni': alumni})

@user_passes_test(is_admin)
@login_required(login_url='signin')
def admin_student_list(request):
    students = StudentProfile.objects.all()
    return render(request, 'student_list.html', {'students': students})

@login_required(login_url='signin')
def admin_job_list(request):
    jobs = JobPost.objects.all()
    return render(request, 'job_list.html', {'jobs': jobs})

@login_required(login_url='signin')
def admin_gallery_list(request):
    gallery = Photo.objects.all()
    return render(request, 'gallery_list.html', {'gallery': gallery})


# List all alumni
@login_required(login_url='signin')
def alumni_list(request):
    alumni_profiles = AlumniProfile.objects.select_related('user').all()
    return render(request, 'user_alumni_list.html', {'alumni_profiles': alumni_profiles})

# List all students
@login_required(login_url='signin')
def student_list(request):
    student_profiles = StudentProfile.objects.select_related('user').all()
    return render(request, 'user_student_list.html', {'student_profiles': student_profiles})

# Detail view for alumni
@login_required(login_url='signin')
def alumni_detail(request, username):
    alumni = get_object_or_404(AlumniProfile, user__username=username)
    return render(request, 'alumni_detail.html', {'alumni': alumni})

# Detail view for student
@login_required(login_url='signin')
def student_detail(request, username):
    student = get_object_or_404(StudentProfile, user__username=username)
    return render(request, 'student_detail.html', {'student': student})



@login_required(login_url='signin')
def combined_user_list(request):
    alumni_profiles = AlumniProfile.objects.select_related('user')
    student_profiles = StudentProfile.objects.select_related('user')

    return render(request, 'combined_user_list.html', {
        'alumni_profiles': alumni_profiles,
        'student_profiles': student_profiles,
    })


def view_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Try to get the user's profile from either Alumni or Student
    profile = None
    profile_type = None

    try:
        profile = AlumniProfile.objects.get(user=user)
        profile_type = "alumni"
    except AlumniProfile.DoesNotExist:
        try:
            profile = StudentProfile.objects.get(user=user)
            profile_type = "student"
        except StudentProfile.DoesNotExist:
            profile = None

    if not profile:
        return render(request, 'profile_not_found.html', {'user': user})

    return render(request, 'profile_detail.html', {
        'profile': profile,
        'profile_type': profile_type
    })