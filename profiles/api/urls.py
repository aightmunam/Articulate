from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import ProfileViewSet

profile_list = ProfileViewSet.as_view({
    'get': 'list'
})

profile_detail = ProfileViewSet.as_view({
    'get': 'retrieve'
})

profile_detail_username = ProfileViewSet.as_view({
    'get': 'retrieve'
}, lookup_field='username')

app_name = "profiles"
urlpatterns = [
    path('', profile_list, name='profile-list'),
    path('<int:pk>/', profile_detail, name='profile-detail'),
    path('@<slug:username>/', profile_detail_username, name='profile-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
