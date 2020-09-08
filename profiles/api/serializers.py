from rest_framework import serializers

from ..models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['username', 'bio', 'first_name', 'display', 'last_name', 'following', 'followers', 'followed_profiles', 'favorite_articles', 'authored_articles']
        read_only_fields = ('username',)


    def get_following(self, instance):
        return instance.get_followed_profiles().count()

    def get_followers(self, instance):
        return instance.get_followers().count()


