from rest_framework import generics, renderers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from articles.models import Article
from articles.api.serializers import ArticleSerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'articles': reverse('api_articles:article-list', request=request, format=format),
        'profiles': reverse('api_profiles:profile-list', request=request, format=format)
    })


class ArticleList(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


class ArticleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
