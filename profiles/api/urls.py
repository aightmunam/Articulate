from django.contrib import admin
from django.urls import path, include

from rest_framework.urlpatterns import format_suffix_patterns

from .views import ProfileList, ProfileDetail

app_name = "profiles"
urlpatterns = [
    path('', ProfileList.as_view(), name='profile-list'),
    path('<int:pk>/', ProfileDetail.as_view(), name='profile-detail'),
    path('@<slug:username>/', ProfileDetail.as_view(lookup_field = 'username'), name='profile-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
