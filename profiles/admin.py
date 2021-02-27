from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfieAdmin(admin.ModelAdmin):
    list_display = ('username', 'bio')
