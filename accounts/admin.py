from django.contrib import admin
from accounts.models import Department, UserProfile

# Register your models here.
admin.site.register(Department)
admin.site.register(UserProfile)