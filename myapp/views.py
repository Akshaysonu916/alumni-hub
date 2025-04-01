from django.shortcuts import render,redirect,get_object_or_404
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout,login,authenticate

# Create your views here.

@login_required(login_url='signin')
def add_job(request):
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('jobpost_list')  # Redirect to the job post list page
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
    jobs = JobPost.objects.all()  # Fetch all job posts
    return render(request, 'jobpost_list.html', {'jobs': jobs})

def userjobs_view(request):
    jobs = JobPost.objects.all()
    return render(request, 'userjobs.html', {'jobs': jobs})

def job_post_detail(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)
    return render(request, 'jobpost_detail.html', {'job': job})


def edit_jobpost(request, job_id):
    jobpost = get_object_or_404(JobPost, id=job_id)
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