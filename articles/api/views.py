from rest_framework import permissions, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from articles.api.serializers import ArticleSerializer
from articles.models import Article


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'articles': reverse('api_articles:article-list', request=request, format=format),
        'profiles': reverse('api_profiles:profile-list', request=request, format=format)
    })


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)