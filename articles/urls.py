from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'articles'
urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('new/', views.article_create_new, name='article_create_new'),
    path('<int:article_id>/<slug:article_slug>/', views.article_detail, name='article_detail'),
]
