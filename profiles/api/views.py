from rest_framework import viewsets

from profiles.api.serializers import ProfileSerializer
from profiles.models import Profile


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
