from django.shortcuts import render,redirect
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout,login,authenticate

# Create your views here.

# @login_required(login_url='signin')
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
    if request.method == 'POST':
        print('working signup')
        errors={}
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        print('email',email)
        print('username',username)
        print('password',password)
        print('confirm password',confirm_password)

        if password!=confirm_password:
            errors["confirm_password"]="Password do not match!"
        print('password validation completerd')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'username is already taken')
            print('email already taken')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already taken')
            print('email already taken')
            
        if errors:
            return render(request,'signup.html',{'errors':errors})

        User.objects.create_user(
        email=email,
        username=username,
        password=password,   
        )
        print('created')
        messages.success(request, 'Account created successfully. Please log in.')
        return redirect('signin')
    return render(request,'signup.html')


def signin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        print(user)
        if user:
            login(request, user)
            if user.is_superuser:
                return redirect('jobpost_list')
            else:
                return redirect('home')


        else:
            messages.error(request, 'Invalid username or password')
            return redirect('signin')
    return render(request,'signin.html')

def home_view(request):

    return render(request,'home.html',{'user':request.user})


def logout_view(request):
    logout(request)
    return redirect('signin')


def jobpost_list(request):
    jobs = JobPost.objects.all()  # Fetch all job posts
    return render(request, 'jobpost_list.html', {'jobs': jobs})