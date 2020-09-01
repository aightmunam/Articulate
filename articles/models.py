import os

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count
from django_extensions.db.fields import AutoSlugField
from django.conf import settings

from .signals import tag_click


class Article(models.Model):
    title = models.CharField(max_length=100)
    slug = AutoSlugField(('slug'), max_length=50, unique=True, populate_from=('title',))
    description = models.CharField(max_length=300)
    content = models.TextField()
    # blank = True means not required in Django
    # null = True means not required in the database
    cover_image = models.ImageField(upload_to="article-cover/", blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='authored_articles')
    tags = models.ManyToManyField('articles.Tag', related_name='articles', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_similar_articles(self):
        article_tags = self.tags.values_list('id', flat=True)
        similar_articles = Article.objects.filter(tags__in=article_tags).exclude(id=self.id)
        similar_articles = similar_articles.annotate(same_tags=Count('tags')).order_by('-same_tags', '-created_at')
        return similar_articles

    def get_all_comments(self):
        return self.comments.all().order_by('-created_at')

    def get_authors_favorited(self):
        return self.favorited.all()

    def get_favorited_count(self):
        return len(self.get_authors_favorited())


class Tag(models.Model):
    name = models.CharField(max_length=25, unique=True)
    slug = AutoSlugField(('slug'), max_length=25, populate_from=('name',))
    click_count = models.IntegerField(default=0)
    clicked_by_profile = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                                related_name='tags_clicked',
                                                blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def increase_click_count(self):
        self.click_count += 1
        self.save()

    def add_profile_to_clicked(self, Profile):
        self.clicked_by_profile.add(Profile)
        self.save()


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               related_name='comments')

    article = models.ForeignKey(Article,
                                on_delete=models.CASCADE,
                                related_name='comments')

    body = models.TextField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return "Comment by {} on {}".format(self.author, self.article)