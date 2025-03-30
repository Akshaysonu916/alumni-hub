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
            return redirect('signin')  # Redirect to login after successful signup
    else:
        form = SignUpForm()  # Ensure 'form' is always defined

    return render(request, 'signup.html', {'form': form})

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

@login_required(login_url='signin')
def jobpost_list(request):
    jobs = JobPost.objects.all()  # Fetch all job posts
    return render(request, 'jobpost_list.html', {'jobs': jobs})

def userjobs_view(request):
    jobs = JobPost.objects.all()
    return render(request, 'userjobs.html', {'jobs': jobs})

def job_post_detail(request, pk):
    job = get_object_or_404(JobPost, pk=pk)
    return render(request, 'jobpost_detail.html', {'job': job})


# View to display the photo gallery
@login_required(login_url='signin')
def photo_gallery(request):
    photos = Photo.objects.all().order_by('-upload_date')  # Fetch all photos, ordered by upload date
    return render(request, 'photo_gallery.html', {'photos': photos})

# View to handle photo uploads
def upload_photo(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            form.save()  # Save the uploaded photo to the database
            return redirect('photo_gallery')  # Redirect to the gallery page after upload
    else:
        form = PhotoForm()  # Render an empty form for GET requests
    return render(request, 'upload_photo.html', {'form': form})