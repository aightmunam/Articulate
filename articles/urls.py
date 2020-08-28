from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'articles'
urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('local-feed/', views.article_list, {'local': True}, name='article_local_feed'),
    path('local-feed/tag/<slug:tag_slug>/', views.article_list, {'local': True}, name='article_local_feed_by_tag'),
    path('tag/<slug:tag_slug>/', views.article_list, name='article_list_by_tag'),
    path('search/<slug:query>/', views.article_list, name='article_list_by_search'),
    path('new/', views.article_create_new, name='article_create_new'),
    path('<slug:article_slug>/', views.article_detail, name='article_detail'),
    path('<slug:article_slug>/edit/', views.article_edit, name='article_edit'),
    path('<slug:article_slug>/delete/', views.article_delete, name='article_delete'),
    path('<slug:article_slug>/favorite/', views.article_favorite, {"favorite": True}, name='article_favorite'),
    path('<slug:article_slug>/unfavorite/', views.article_favorite, {"favorite": False}, name='article_unfavorite'),
    path('<slug:article_slug>/comments/<int:comment_id>/delete', views.article_delete_comment, name='article_delete_comment')
]
