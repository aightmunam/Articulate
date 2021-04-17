from django.conf.urls import url
from django.urls import include, path

from . import views

app_name = 'profiles'
urlpatterns = [
    path('login/', views.profile_login, name='profile_login'),
    path('register/', views.profile_register, name='profile_register'),
    path('logout/', views.profile_logout, name='profile_logout'),
    path('@<str:username>/', views.profile_detail, name='profile_detail'),
    path('@<str:username>/follow/', views.profile_follow, {"follow": True}, name='profile_follow'),
    path('@<str:username>/unfollow/', views.profile_follow, {"follow": False}, name='profile_unfollow'),
    path('@<str:username>/edit/', views.profile_edit, name='profile_edit'),
    path('@<str:username>/favorites/', views.profile_favorites, name='profile_favorites'),
]
