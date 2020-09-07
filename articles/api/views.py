from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.exceptions import NotFound

from articles.models import Article
from articles.api.serializers import ArticleSerializer



class ArticleList(APIView):
    def get(self, request, format=None):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        article_serializer = ArticleSerializer(data=request.data)
        if article_serializer.is_valid():
            article_serializer.save()
            return Response(article_serializer.data, status=status.HTTP_201_CREATED)
        return Response(article_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleDetail(APIView):
    def get_object(self, article_slug):
        try:
            return Article.objects.get(slug=article_slug)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')

    def get(self, request, article_slug, format=None):
        current_article = self.get_object(article_slug)
        current_article_serializer = ArticleSerializer(current_article)
        return Response(current_article_serializer.data, status=status.HTTP_200_OK)

    def update(self, request, article_slug, format=None):
        current_article = self.get_object(article_slug)

        data = JSONParser().parse(request)
        current_article_serializer = ArticleSerializer(current_article, data=data)
        if current_article_serializer.is_valid():
            current_article_serializer.save()
            return Response(current_article_serializer.data, status=status.HTTP_200_OK)
        return Response(current_article_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, article_slug, format=None):
        current_article = self.get_object(article_slug)

        is_delete_successful = current_article.delete()
        if is_delete_successful:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
