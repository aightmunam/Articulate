"""
Admin for articles app
"""
from django.contrib import admin

from .models import Article, Comment, Tag


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Admin for Article
    """
    list_display = ('title', 'description', 'created_at')
    search_fields = ('title', 'body')
    raw_id_fields = ('author',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin for Tag
    """
    list_display = ('name', 'created_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin for Comment
    """
    list_display = ('author', 'article', 'body', 'created_at')
