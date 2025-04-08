from django.shortcuts import render,redirect,get_object_or_404
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required ,user_passes_test
from django.contrib import messages
from django.contrib.auth import logout,login,authenticate
from django.http import HttpResponseForbidden
from django.db.models import Q

# Create your views here.

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
    return render(request, 'add_job.html', {'form': form})


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

def signin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully signed in.")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('signin')

    return render(request, 'signin.html')

def home_view(request):
    return render(request,'home.html',{'user':request.user})


def logout_view(request):
    logout(request)
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

# @login_required
# def create_profile_view(request):
#     if request.method == "POST":
#         user_type = request.POST.get("user_type")
        
#         if user_type == "alumni":
#             company = request.POST.get("company", "")
#             job_title = request.POST.get("job_title", "")
#             graduation_year = request.POST.get("graduation_year", 2025)
#             linkedin = request.POST.get("linkedin", "")
            
#             AlumniProfile.objects.create(
#                 user=request.user,
#                 company=company,
#                 job_title=job_title,
#                 graduation_year=graduation_year,
#                 linkedin=linkedin
#             )
        
#         elif user_type == "student":
#             enrollment_year = request.POST.get("enrollment_year")
#             major = request.POST.get("major", "")
            
#             # Ensure enrollment_year is provided before creating the profile
#             if not enrollment_year:
#                 messages.error(request, "Enrollment year is required for students.")
#                 return render(request, "create_profile.html")
            
#             StudentProfile.objects.create(
#                 user=request.user,
#                 enrollment_year=enrollment_year,
#                 major=major
#             )

#         return redirect("profile")  # Redirect to profile page after creation

#     return render(request, "create_profile.html")



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





def admin_alumni_list(request):
    alumni = AlumniProfile.objects.all()
    return render(request, 'alumni_list.html', {'alumni': alumni})

def admin_student_list(request):
    students = StudentProfile.objects.all()
    return render(request, 'student_list.html', {'students': students})

def admin_job_list(request):
    jobs = JobPost.objects.all()
    return render(request, 'job_list.html', {'jobs': jobs})

def admin_gallery_list(request):
    gallery = Photo.objects.all()
    return render(request, 'gallery_list.html', {'gallery': gallery})