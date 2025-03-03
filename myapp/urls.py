from django.urls import path
from .views import *

urlpatterns = [
    path('',home_view,name='home'),
    path('signin/',signin_view,name='signin'),
    path('signup/',signup_view,name='signup'),
    path('signout/',logout_view,name='signout'),
]
