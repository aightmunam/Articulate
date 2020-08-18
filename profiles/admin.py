from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Profile



# Register your models here.
@admin.register(Profile)
class ProfieAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
