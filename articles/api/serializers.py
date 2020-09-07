from rest_framework import serializers

from ..models import Article, Tag, Comment

class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='profiles.Profile.username')
    class Meta:
        model = Article
        fields = ['id', 'title', 'description', 'content', 'cover_image', 'created_at', 'author']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name', 'created_at', 'updated_at']