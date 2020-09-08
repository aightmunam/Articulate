from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from articles.models import Article
from django.db.models import Count
from django.db.models.signals import post_delete
from django.dispatch import receiver



class Profile(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    bio = models.CharField(max_length=100)
    display = models.ImageField(upload_to="profile-display/")
    followed_profiles = models.ManyToManyField(
        "self", related_name="followers", blank=True, symmetrical=False)
    favorite_articles = models.ManyToManyField(
        "articles.Article", related_name="favorited", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    def get_authored_articles(self):
        return self.authored_articles.all()

    def get_favorite_articles(self):
        return self.favorite_articles.all()

    def get_followed_profiles(self):
        return self.followed_profiles.all()

    def get_followers(self):
        return self.followers.all()

    def follow_profile(self, username):
        profile_to_follow = Profile.objects.get(username=username)
        if profile_to_follow:
            self.followed_profiles.add(profile_to_follow)

    def unfollow_profile(self, username):
        if self.followed_profiles.filter(username=username).exists():
            self.followed_profiles.remove(self.followed_profiles.get(username=username))

    def is_favorite(self, article_slug):
        if self.favorite_articles.filter(slug=article_slug).exists():
            return True
        return False

    def favorite_article(self, article_slug):
        article_to_favorite = Article.objects.get(slug=article_slug)
        if article_to_favorite and not self.is_favorite(article_slug):
            self.favorite_articles.add(article_to_favorite)

    def unfavorite_article(self, article_slug):
        if self.is_favorite(article_slug):
            self.favorite_articles.remove(self.favorite_articles.get(slug=article_slug))

    def get_follower_count(self):
        return self.get_followers().count()

    def get_following_count(self):
        return self.get_followed_profiles().count()
