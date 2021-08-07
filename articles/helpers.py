"""
Helpers for articles app
"""
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Count, Q

from articles.models import Article, Tag


def get_articles_liked_and_authored_by_followed_profiles(user):
    """
    Given a user, returns a querset of articles that are either authored or favourited by
    the followed profiles by the user

    Args:
        user (Profile): User for which to get the feed articles

    Returns:
        QuerySet: A QuerySet containing articles
    """
    followed_profile_ids = user.followed_profiles.all().values_list('id', flat=True)
    user_with_followed_profiles = list(followed_profile_ids) + [user.id]

    return Article.objects.select_related('author').prefetch_related('tags').filter(
        Q(author_id__in=followed_profile_ids) | Q(favorited__in=user_with_followed_profiles)
    ).distinct().order_by('-created_at')


def get_top_n_most_popular_tags(articles, top_n):
    """
    Given a queryset of Articles, returns the top_n most popular tags in the articles
    contained in the queryset

    Args:
        articles (QuerySet): QuerySet containing articles
        top_n (int): Top n tags to return

    Returns
        QuerySet: Queryset containing the top_n tags
    """
    tags_sorted_on_popularity = Tag.objects.filter(articles__in=articles).annotate(
        popularity=Count('id')).order_by('-popularity')

    return tags_sorted_on_popularity[:top_n + 1]


def get_articles_tagged_by_given_tag(articles, tag_slug):
    """
    Given a queryset of articles, return only the articles tagged by a Tag with slug, `tag_slug`

    Args:
        articles (QuerySet): QuerySet containing articles
        tag_slug (str): Tag slug

    Returns:
        QuerySet: Queryset containing articles marked by tag_slug Tags
    """
    return articles.filter(tags__slug=tag_slug)


def get_most_similar_articles_based_on_trigram_similarity(query):
    """
    Given a query, returns all the articles based on trigram similarity

    Args:
        query (str): Query to search articles for

    Returns:
        QuerySet: A queryset of similar articles
    """
    return Article.objects.annotate(similarity=TrigramSimilarity('title', query)).filter(
        similarity__gt=0.1).order_by('-similarity')
