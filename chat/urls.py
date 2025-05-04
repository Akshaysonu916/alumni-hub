from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 
urlpatterns = [
        path('chat/<str:room_name>/', views.chat_room, name='chat'),
        
]
