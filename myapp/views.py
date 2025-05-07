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
from .models import Connection, User
from datetime import datetime


# Create your views here.

# def is_alumni(user):
    #  return user.is_authenticated and user.profile.user_type == 'alumni'


# @user_passes_test(is_alumni)

@login_required(login_url='signin')
def add_job(request):
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user  # ✅ Track who posted the job
            job.save()

            # ✅ Notify all users EXCEPT the one who posted the job
            users_to_notify = User.objects.exclude(id=request.user.id)

            for user in users_to_notify:
                Notification.objects.create(
                    user=user,
                    message=f"{request.user.username} posted a new job: {job.job_name}",
                    notification_type='job'
                )

            return redirect('jobpost_list')  # ✅ Redirect to job list page
    else:
        form = JobPostForm()

    # 🔔 Connection request notifications for header/navbar
    connection_notifications = Connection.objects.filter(to_user=request.user, is_accepted=False)
    count = connection_notifications.count()

    return render(request, 'addjobs.html', {
        'form': form,
        'connection_notifications': connection_notifications,
        'count': count,
    })

@login_required
def notifications_view(request):
    # Get all notifications for the user
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Mark all as read
    notifications.update(is_read=True, read_at=timezone.now())

    return render(request, 'notification.html', {
        'notifications': notifications,
        'notification_count': 0  # Already marked as read
    })


@login_required
def my_notifications(request):
    # Show all notifications, grouped by type if desired
    notifications = request.user.notifications.order_by('-created_at')
    return render(request, 'notification.html', {'notifications': notifications})


@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return HttpResponseRedirect(reverse('my_notifications'))


@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()
    return HttpResponseRedirect(reverse('my_notifications'))


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
    connection_notifications = Connection.objects.none()  # default to empty QuerySet

    if request.user.is_authenticated:
        connection_notifications = Connection.objects.filter(
            to_user=request.user,
            is_accepted=False
        )
    
    context = {
        'connection_notifications': connection_notifications,
        'unread_notifications_exist': connection_notifications.exists(),  # ✅ Fixed: now safe
        # other context variables...
    }
    return render(request, 'home.html', context)



def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully signout.")
    return redirect('signin')



#job posts all operations
@login_required(login_url='signin')
def jobpost_list(request):
    query = request.GET.get("q")

    # 🔎 Job filtering based on the search query
    if query:
        jobs = JobPost.objects.filter(Q(job_name__icontains=query))
    else:
        jobs = JobPost.objects.all()

    # 🔔 Connection notifications
    connection_notifications = Connection.objects.filter(to_user=request.user, is_accepted=False)
    connection_count = connection_notifications.count()

    # 📩 Unread general notifications (for students only)
    unread_count = 0
    if hasattr(request.user, 'student_profile'):
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True, read_at=timezone.now())

    return render(request, 'jobpost_list.html', {
        'jobs': jobs,
        'connection_notifications': connection_notifications,
        'count': connection_count,
        'unread_notifications_count': unread_count,
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
            # messages.success(request, 'Job post updated successfully.')
            return redirect('jobpost_detail', job_id=jobpost.id)
    else:
        form = JobPostForm(instance=jobpost)

    return render(request, 'edit_jobpost.html', {'form': form, 'jobpost': jobpost})


def delete_jobpost(request, job_id):
    jobpost = get_object_or_404(JobPost, id=job_id)
    if request.method == 'POST':
        jobpost.delete()
        # messages.success(request, 'Job post deleted successfully.')
        return redirect('jobpost_list')
    return render(request, 'confirm_delete.html', {'jobpost': jobpost})

# photos sections
# View to display the photo gallery
@login_required(login_url='signin')
def photo_gallery(request):
    photos = Photo.objects.all().order_by('-upload_date')  # Ordered by upload date

    # 🔔 Connection notifications
    connection_notifications = Connection.objects.filter(to_user=request.user, is_accepted=False)
    connection_count = connection_notifications.count()

    return render(request, 'photo_gallery.html', {
        'photos': photos,
        'connection_notifications': connection_notifications,
        'count': connection_count,
    })


# View to handle photo uploads
def upload_photo(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)  # Don't save to DB yet
            photo.user = request.user         # Assign logged-in user
            photo.save()                      # Now save to DB
            # messages.success(request, "Photo uploaded successfully!")
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
            # messages.success(request, "Photo updated successfully!")
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
        # messages.success(request, "Photo deleted successfully!")
        return redirect('photo_gallery')

    return render(request, 'delete_photo.html', {'photo': photo})


@login_required
def profile_view(request):
    """Display the profile of the logged-in user based on their role."""
    try:
        # Try to fetch the profile based on the user's role
        if hasattr(request.user, 'alumni_profile'):
            profile = request.user.alumni_profile
            template = "alumni_profile.html"  # Template for alumni profile
        elif hasattr(request.user, 'student_profile'):
            profile = request.user.student_profile
            template = "student_profile.html"  # Template for student profile
        else:
            # Redirect to edit profile if no profile exists
            return redirect("edit_profile")

        # Get the unread connection notifications
        connection_notifications = Connection.objects.filter(to_user=request.user, is_accepted=False)
        connection_count = connection_notifications.count()

        # Render the appropriate template with the context
        return render(request, template, {
            "profile": profile,
            "connection_notifications": connection_notifications,
            "count": connection_count,
        })

    except Exception as e:
        # Handle any unexpected errors and redirect to profile edit
        print(f"Error loading profile: {e}")
        return redirect("edit_profile")
    
@login_required    
def edit_profile_view(request):
    user = request.user

    # Determine profile and form class
    if hasattr(user, 'is_alumni') and user.is_alumni:
        profile, created = AlumniProfile.objects.get_or_create(user=user)
        form_class = AlumniProfileForm
    elif hasattr(user, 'is_student') and user.is_student:
        profile, created = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'enrollment_year': 2020,
            }
        )
        form_class = StudentProfileForm
    else:
        return HttpResponseForbidden("Invalid user type or missing profile.")

    # Handle POST
    if request.method == "POST":
        if 'add_skill' in request.POST:
            # Handle skill addition
            skill_form = SkillForm(request.POST)
            form = form_class(instance=profile)  # Retain profile form
            if skill_form.is_valid():
                skill = skill_form.save(commit=False)
                skill.alumni = user
                skill.save()
                return redirect("edit_profile")
        else:
            # Handle profile update
            form = form_class(request.POST, request.FILES, instance=profile)
            skill_form = SkillForm()
            if form.is_valid():
                form.save()
                return redirect("profile")
    else:
        form = form_class(instance=profile)
        skill_form = SkillForm()

    # Fetch existing skills
    skills = Skill.objects.filter(alumni=user)

    return render(request, "edit_profile.html", {
        "form": form,
        "skill_form": skill_form,
        "skills": skills,
    })




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
def view_alumni_profile(request, alumni_id):
    alumni = get_object_or_404(AlumniProfile, id=alumni_id)
    return render(request, 'adminalumni_profile.html', {'alumni': alumni})

@user_passes_test(is_admin)
def delete_alumni(request, alumni_id):
    alumni = get_object_or_404(AlumniProfile, id=alumni_id)
    if request.method == 'POST':
        alumni.user.delete()  # Deletes both Alumni and linked User if related via OneToOneField
        # messages.success(request, "Alumni deleted successfully.")
        return redirect('admin_alumni_list')  # Replace with your actual alumni list view name
    return redirect('admin_alumni_list')


@user_passes_test(is_admin)
@login_required(login_url='signin')
def admin_student_list(request):
    students = StudentProfile.objects.all()
    return render(request, 'student_list.html', {'students': students})

@user_passes_test(is_admin)
def view_student_profile(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    return render(request, 'adminstudent_profile.html', {'student': student})

@user_passes_test(is_admin)
def delete_student(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    if request.method == 'GET':
        user = student.user
        student.delete()
        user.delete()
        # messages.success(request, 'Student deleted successfully.')
    return redirect('admin_student_list')  # replace with your actual student list URL name


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
# Adjust as per your app structure
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
    connection_notifications = received_connections
    connection_notifications = Connection.objects.filter(to_user=request.user, is_accepted=False)
    count = connection_notifications.count()

    return render(request, 'combined_user_list.html', {
        'alumni_profiles': alumni_profiles,
        'student_profiles': student_profiles,
        'sent_requests': sent_ids,
        'received_requests': received_ids,
        'connected_ids': connected_ids,
        'received_connections': received_connections,
        'connection_notifications': connection_notifications,
        'count': count # Pass connections for accepting
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
    target_user = get_object_or_404(User, id=user_id)
    from_user = request.user

    if request.method == 'POST':
        # Prevent self-connections and duplicate requests
        if from_user != target_user and not Connection.objects.filter(from_user=from_user, to_user=target_user).exists():
            # Create connection request
            Connection.objects.create(from_user=from_user, to_user=target_user, is_accepted=False)

            # Create connection notification
            Notification.objects.create(
                user=target_user,
                message=f"{from_user.username} sent you a connection request.",
                notification_type='connection'
            )

    # return redirect('student_profile', user_id=user_id)

    # return redirect('some_view')

    return redirect('combined_user_list')  # 🔄 Update if needed to your actual view name

@login_required
def accept_connection_request(request, connection_id):
    # Fetch the connection request
    connection = get_object_or_404(Connection, id=connection_id, to_user=request.user)

    # If the connection is not already accepted
    if not connection.is_accepted:
        connection.is_accepted = True  # Mark as accepted
        connection.save()

        # Notify the sender that their request was accepted
        Notification.objects.create(
            user=connection.from_user,  # The receiver of the notification (the sender of the request)
            message=f"{request.user.username} has accepted your connection request.",  # Message content
            notification_type='connection_accepted'  # Type set to 'connection_accepted'
        )

    # Redirect to the combined user list or other page after accepting the request
    return redirect('combined_user_list')  # 🔁 Replace with your actual redirect view name


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
    # messages.success(request, "You have successfully disconnected.")

    # Redirect to the users page or wherever you need
    return redirect('combined_user_list')

@login_required
def cancel_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    connection = Connection.objects.filter(from_user=request.user, to_user=to_user, is_accepted=False).first()
    if connection:
        connection.delete()
    return redirect('combined_user_list')  # or your actual user list view name

# @login_required
# def mark_notifications_as_read(request):
#     # Mark all notifications for the user as read
#     request.user.notifications.filter(is_read=False).update(is_read=True)
#     return redirect('combined_user_list')  # Or any other redirect

# def base_context(request):
#     job_notifications = request.user.notifications.filter(type='job', is_read=False)
#     connection_notifications = request.user.notifications.filter(type='connection', is_read=False)
    
#     return {
#         'job_notifications': job_notifications,
#         'connection_notifications': connection_notifications,
#     }
@login_required
def connect_requests(request):
    connection_requests = Connection.objects.filter(to_user=request.user, is_accepted=False)
    return render(request, 'connect_requests.html', {'connection_requests': connection_requests})

def student_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)

    # Include connection notifications if the user is authenticated
    connection_notifications = []
    if request.user.is_authenticated:
        connection_notifications = Connection.objects.filter(
            to_user=request.user,
            is_accepted=False
        )

    return render(request, 'student_profile.html', {
        'profile_user': profile_user,
        'connection_notifications': connection_notifications,
    })


def edit_profile(request):
    if request.method == 'POST':
        skill_form = SkillForm(request.POST)
        if skill_form.is_valid():
            skill = skill_form.save(commit=False)
            skill.alumni = request.user
            skill.save()
            return redirect('edit_profile')  # or 'profile' depending on your flow
    else:
        skill_form = SkillForm()

    skills = Skill.objects.filter(alumni=request.user)
    return render(request, 'edit_profile.html', {
        'skill_form': skill_form,
        'skills': skills,
    })

def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, alumni=request.user)
    skill.delete()
    return redirect('edit_profile')

# Edit Skill
def edit_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, alumni=request.user)

    if request.method == "POST":
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            return redirect('edit_profile')
    else:
        form = SkillForm(instance=skill)

    return render(request, "edit_skill.html", {"form": form, "skill": skill})




def about_us(request):
    return render(request, 'about_us.html')

def support(request):
    return render(request, 'support.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_of_service(request):
    return render(request, 'terms_of_service.html')