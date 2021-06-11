"""
Urls for articles app
"""
from django.urls import path, re_path

from . import views

app_name = 'articles'
urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('local-feed/', views.ArticleListView.as_view(), {'local': True}, name='article_local_feed'),
    path('local-feed/tag/<slug:tag_slug>/', views.ArticleListView.as_view(), {'local': True},
         name='article_local_feed_by_tag'),
    path('tag/<slug:tag_slug>/', views.ArticleListView.as_view(), name='article_list_by_tag'),
    path('search/<slug:query>/', views.ArticleListView.as_view(), name='article_list_by_search'),
    path('new/', views.ArticleCreateView.as_view(), name='article_create_new'),
    path('<slug:article_slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('<slug:article_slug>/edit/', views.ArticleUpdateView.as_view(), name='article_edit'),
    path('<slug:article_slug>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
    re_path('(?P<slug>[-\w]+)/(?P<rate>favourite|unfavourite)/$', views.ArticleRateView.as_view(), name='article_rate'),
    path('<slug:article_slug>/comments/<int:comment_id>/delete', views.CommentDeleteView.as_view(),
         name='article_delete_comment')
]
