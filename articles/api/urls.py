from django.contrib import admin
from django.urls import path, include

from rest_framework.urlpatterns import format_suffix_patterns

from .views import ArticleList, ArticleDetail

app_name = "articles"
urlpatterns = [
    path('', ArticleList.as_view()),
    path('<slug:slug>/', ArticleDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
