from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile



# Register your models here.
@admin.register(Profile)
class ProfieAdmin(admin.ModelAdmin):
    list_display = ('username', 'bio')


# admin.site.register(Profile, UserAdmin)