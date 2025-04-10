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
    path('job_post_detail/<int:job_id>/',job_post_detail, name='jobpost_detail'),
    path('gallery/',photo_gallery, name='photo_gallery'),
    path('upload/',upload_photo, name='upload_photo'),
    path('<int:job_id>/edit/', edit_jobpost, name='edit_jobpost'),
    path('<int:job_id>/delete/',delete_jobpost, name='delete_jobpost'),
    path('photo/<int:id>/',photo_detail, name='photo_detail'),
    path('photo/<int:id>/edit/', edit_photo, name='edit_photo'),
    path('photo/<int:id>/delete/', delete_photo, name='delete_photo'),
    path('profile/', profile_view, name='profile'),  
    path("profile/edit/", edit_profile_view, name="edit_profile"),
    # path("profile/create/", create_profile_view, name="create_profile"),
    path('admin-dashboard/',admin_dashboard, name='admin_dashboard'),
    path('alumni/', admin_alumni_list, name='admin_alumni_list'),
    path('students/', admin_student_list, name='admin_student_list'),
    path('jobs/', admin_job_list, name='admin_job_list'),
    path('gallery/', admin_gallery_list, name='admin_gallery_list'),
]
