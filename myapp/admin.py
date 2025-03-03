from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(AlumniProfile)
admin.site.register(StudentProfile)
admin.site.register(JobPost)
admin.site.register(Event)
admin.site.register(ChatMessage)
