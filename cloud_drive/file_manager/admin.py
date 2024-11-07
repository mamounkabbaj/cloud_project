from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import UserFile

# Register the UserFile model to make it visible in the Admin panel
admin.site.register(UserFile)