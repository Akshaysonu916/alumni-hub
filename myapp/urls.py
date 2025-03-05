from django.urls import path
from .views import *

urlpatterns = [
    path('',home_view,name='home'),
    path('signin/',signin_view,name='signin'),
    path('signup/',signup_view,name='signup'),
    path('signout/',logout_view,name='signout'),
    path('jobs/',jobpost_list,name='jobpost_list'),
    path('add/',add_job,name='add_jobs'),
    path('userjobs/',userjobs_view, name='userjobs'),
    path('job_post_detail/<int:pk>/', job_post_detail, name='jobpost_detail'),
    path('gallery/',photo_gallery, name='photo_gallery'),
    path('upload/',upload_photo, name='upload_photo'),
]
