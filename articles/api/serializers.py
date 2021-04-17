from rest_framework import serializers

from profiles.api.serializers import ProfileSerializer

from ..models import Article, Comment, Tag


class ArticleSerializer(serializers.ModelSerializer):
    # author = ProfileSerializer(read_only=True)
    has_favorited = serializers.SerializerMethodField(method_name = "is_favorite")
    favorites_count = serializers.SerializerMethodField()


    class Meta:
        model = Article
        fields = ['id', 'slug', 'title', 'description', 'content', 'cover_image', 'created_at', 'author', 'favorites_count', 'has_favorited']

    def is_favorite(self, instance):
        request = self.context.get('request', None)

        if request:
            if request.user.is_authenticated:
                return request.user.is_favorite(instance.slug)
        return False

    def get_favorites_count(self, instance):
        return instance.get_favorited_count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name', 'created_at', 'updated_at']


    def to_representation(self, obj):
        return obj.tag