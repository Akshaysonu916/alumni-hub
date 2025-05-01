from django.shortcuts import render,redirect,get_object_or_404
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required ,user_passes_test
from django.contrib import messages
from django.contrib.auth import logout,login,authenticate,get_user_model
from django.http import HttpResponseForbidden,HttpResponseRedirect
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse


# Create your views here.

# def is_alumni(user):
#     return user.is_authenticated and user.profile.user_type == 'alumni'

def post_job(request):
    if request.method == 'POST':
        # Your job posting logic...

        # Notify all users except the poster
        users_to_notify = User.objects.exclude(id=request.user.id).filter(user_type__in=['student', 'alumni'])

        users_to_notify = User.objects.exclude(id=request.user.id)

        for user in users_to_notify:
            Notification.objects.create(
                user=user,
                message=f"{request.user.username} posted a new job."
            )

        return redirect('job_list')  # or wherever you go after posting

# @user_passes_test(is_alumni)
@login_required(login_url='signin')
def add_job(request):
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()

            # Notify all users except the poster
            users_to_notify = User.objects.exclude(id=request.user.id)
            for user in users_to_notify:
                Notification.objects.create(
                    user=user,
                    message=f"{request.user.username} posted a new job: {job.job_name}",
                    job=job
                )
            return redirect('jobpost_list')
    else:
        form = JobPostForm()
    return render(request, 'addjobs.html', {'form': form})


@login_required
def my_notifications(request):
    notifications = request.user.notifications.order_by('-created_at')
    return render(request, 'notification.html', {'notifications': notifications})


def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    
    # Mark notifications as read
    notifications.update(is_read=True)
    
    notification_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    return render(request, 'notifications.html', {
        'notifications': notifications,
        'notification_count': notification_count
    })

def delete_notification(request, notification_id):
    notification = Notification.objects.get(id=notification_id)
    if notification.user == request.user:
        notification.delete()
    return HttpResponseRedirect(reverse('my_notifications'))  # ✅ correct usag


def some_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    notification_count = notifications.count()
    return render(request, 'notifications.html', {
        'notifications': notifications,
        'notification_count': notification_count,
    })

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
    query = request.GET.get("q")
    if query:
        jobs = JobPost.objects.filter(Q(job_name__icontains=query))
    else:
        jobs = JobPost.objects.all()
    return render(request, 'jobpost_list.html', {'jobs': jobs})
    JobNotification.objects.create(recipient=user, message="New job posted!")
    jobposts = JobPost.objects.all().order_by('-created_at')
    unread_count = 0
    if hasattr(request.user, 'student_profile'):
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True, read_at=timezone.now())

    return render(request, 'jobpost_list.html', {
        'jobposts': jobposts,
        'unread_notifications_count': unread_count
    })


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
    current_user = request.user

    # Fetch profiles, excluding the current user
    alumni_profiles = AlumniProfile.objects.select_related('user').exclude(user=current_user)
    student_profiles = StudentProfile.objects.select_related('user').exclude(user=current_user)

    # Fetch connection data
    sent_requests = Connection.objects.filter(from_user=current_user, is_accepted=False)
    received_requests = Connection.objects.filter(to_user=current_user, is_accepted=False)
    connections = Connection.objects.filter(
        Q(from_user=current_user) | Q(to_user=current_user),
        is_accepted=True
    )

    # Build ID sets
    sent_ids = set(sent_requests.values_list('to_user_id', flat=True))
    received_ids = set(received_requests.values_list('from_user_id', flat=True))
    connected_ids = set()
    for conn in connections:
        connected_ids.add(conn.to_user.id if conn.from_user == current_user else conn.from_user.id)

    # Store the received connections for easy lookup
    received_connections = {conn.from_user.id: conn for conn in received_requests}

    return render(request, 'combined_user_list.html', {
        'alumni_profiles': alumni_profiles,
        'student_profiles': student_profiles,
        'sent_requests': sent_ids,
        'received_requests': received_ids,
        'connected_ids': connected_ids,
        'received_connections': received_connections,  # Pass connections for accepting
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


@login_required
def my_notifications(request):
    # Get notifications in newest-first order
    notifications = request.user.notifications.order_by('-created_at')

    # Mark all unread notifications as read
    request.user.notifications.filter(is_read=False).update(is_read=True)

    return render(request, 'notification.html', {'notifications': notifications})

@login_required
def send_connection_request(request, user_id):
    target_user = User.objects.get(id=user_id)
    if request.method == 'POST':
        Connection.objects.create(from_user=request.user, to_user=target_user)
    return redirect('combined_user_list')

@login_required
def accept_connection_request(request, connection_id):
    # Get the connection object using the connection_id from the URL
    connection = get_object_or_404(Connection, id=connection_id, to_user=request.user, is_accepted=False)

    # Update the connection request to accepted
    connection.is_accepted = True
    connection.save()

    # Redirect after accepting
    return redirect('combined_user_list')  # or any other page you want

@login_required
def remove_connection(request, user_id):
    Connection.objects.filter(
        (models.Q(from_user=request.user, to_user_id=user_id) |
         models.Q(from_user_id=user_id, to_user=request.user))
    ).delete()
    return redirect('combined_user_list')

@login_required
def disconnect_connection(request, user_id):
    # Try to find an accepted connection from the current user to the specified user
    try:
        # Look for an accepted connection either from user to target or from target to user
        connection = Connection.objects.get(
            (Q(from_user=request.user, to_user_id=user_id) | Q(from_user_id=user_id, to_user=request.user)),
            is_accepted=True
        )
    except Connection.DoesNotExist:
        # Handle case where no valid connection exists
        messages.error(request, "No valid connection found to disconnect.")
        return redirect('combined_user_list')  # Redirect back to users list

    # Set the connection status to False to mark as disconnected
    connection.is_accepted = False
    connection.save()

    # Optionally, add a success message
    messages.success(request, "You have successfully disconnected.")

    # Redirect to the users page or wherever you need
    return redirect('combined_user_list')