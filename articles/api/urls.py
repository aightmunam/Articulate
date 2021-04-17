from django.contrib import admin
from django.urls import include, path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import ArticleViewSet, api_root

article_list = ArticleViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

article_detail = ArticleViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

article_detail_slug = ArticleViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
}, lookup_field='slug')

app_name = "articles"
urlpatterns = [
    path('', article_list, name='article-list'),
    path('<int:pk>/', article_detail, name='article-detail'),
    path('<slug:slug>/', article_detail_slug, name='article-detail')
]

urlpatterns = format_suffix_patterns(urlpatterns)
