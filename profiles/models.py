from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=100)
    display = models.ImageField(upload_to="images/profile-display/")
    followed_profiles = models.ManyToManyField(
        "self", related_name="followed", blank=True)
    starred_articles = models.ManyToManyField(
        "articles.Article", related_name="starred", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
