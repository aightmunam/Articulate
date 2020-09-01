import collections

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.db.models import Count
from django.db.models.query import QuerySet
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import TrigramSimilarity
from django.dispatch import receiver

from profiles.models import Profile
from .models import Article, Tag, Comment
from .signals import tag_click
from .forms import ArticleForm, CommentForm, SearchForm


def aritcle_index(request):
    return redirect("articles:article_list")


def article_list(request, tag_slug=None, local=False):
    feed_articles = None
    if local:
        if request.user.is_authenticated:
            current_user_following = request.user.get_followed_profiles()
            local_feed_articles = []

            following_users_authored_articles = [followed_user.get_authored_articles() for followed_user in current_user_following if followed_user]
            if following_users_authored_articles:
                local_feed_articles = following_users_authored_articles[0]
                for followed_user_article_qs in following_users_authored_articles:
                    local_feed_articles = (local_feed_articles | followed_user_article_qs)


            following_users_starred_articles = [followed_user.get_favorite_articles() for followed_user in current_user_following if followed_user]
            if following_users_starred_articles:
                for followed_users_article in following_users_starred_articles:
                    local_feed_articles = (local_feed_articles | followed_users_article)

            if local_feed_articles:
                feed_articles = local_feed_articles.distinct().order_by('-created_at').exclude(author=request.user)
            else:
                feed_articles = local_feed_articles
        else:
            return redirect(settings.LOGIN_URL)
    else:
        global_feed_articles = Article.objects.all().order_by('-created_at')
        feed_articles = global_feed_articles

    tags_in_feed_articles = None
    if feed_articles:
        for article in feed_articles:
            if article:
                if tags_in_feed_articles:
                    tags_in_feed_articles = tags_in_feed_articles | article.tags.all()
                else:
                    tags_in_feed_articles = article.tags.all()
        popular_tags = collections.Counter(tags_in_feed_articles)
        top_five_most_popular_tags = [popular_tag for popular_tag, tag_pop in popular_tags.most_common(5)]
    else:
        top_five_most_popular_tags = []

    search_form = SearchForm()
    tag = None
    query = None
    page = None
    articles = None

    if feed_articles:
        if 'query' in request.GET:
            search_form = SearchForm(request.GET)
            if search_form.is_valid():
                query = search_form.cleaned_data['query']
                feed_articles = Article.objects.annotate(similarity=TrigramSimilarity('title', query),).filter(similarity__gt=0.1).order_by('-similarity')

        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            tag_click.send(sender=Tag, tag=tag, profile=request.user)
            feed_articles = feed_articles.filter(tags__in=[tag])

        paginator = Paginator(feed_articles, 4)
        page = request.GET.get('page')
        try:
            articles = paginator.page(page)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles = paginator.page(paginator.num_pages)

    return render(request, "articles/list.html", context={"page": page,
                                                          "articles": articles,
                                                          "tag": tag,
                                                          "search_form":search_form,
                                                          "query": query,
                                                          "local": local,
                                                          "popular_tags": top_five_most_popular_tags})


def article_detail(request, article_slug):
    article = get_object_or_404(Article, slug=article_slug)
    new_comment = None
    if request.method == 'POST':
        if request.user.is_authenticated:
            comment_form = CommentForm(data=request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.article = article
                new_comment.author = request.user
                new_comment.save()
        else:
            return redirect("profiles:profile_login")
    else:
        comment_form = CommentForm()

    comments = article.get_all_comments()

    paginator = Paginator(comments, 5)
    page = request.GET.get('page')
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)

    return render(request, "articles/detail.html", context={"article": article,
                                                            "page": page,
                                                            "comments": comments,
                                                            "new_comment": new_comment,
                                                            "comment_form": comment_form,})


@login_required
def article_create_new(request):
    if request.method == 'POST':
        form = ArticleForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            tags = form.cleaned_data["tags"]
            tag_list = tags.split(',')
            obj = form.save(commit=False)
            obj.author = request.user
            obj.save()
            for tag in tag_list:
                tag = tag.lower()
                tag_qs = Tag.objects.all().filter(name__icontains=tag)
                if tag_qs:
                    for tag_obj in tag_qs:
                        obj.tags.add(tag_obj)
                else:
                    obj.tags.add(Tag.objects.create(name=tag))

            return redirect('articles:article_detail', article_slug=obj.slug)
    else:
        form = ArticleForm()

    return render(request, "articles/create_new.html", context={"article_form": form})


@login_required
def article_edit(request, article_slug):
    current_article =  get_object_or_404(Article, slug=article_slug)
    if request.method == 'POST':
        form = ArticleForm(data=request.POST, files=request.FILES or None, instance=current_article)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            current_article.title = cleaned_data['title']
            current_article.description = cleaned_data['description']
            current_article.content = cleaned_data['content']
            current_article.cover_image.file = cleaned_data['cover_image']
            current_article.tags.clear()
            tags = cleaned_data["tags"]
            tag_list = tags.split(',')
            for tag in tag_list:
                tag = tag.lower()
                tag_obj, _ = Tag.objects.get_or_create(name=tag)
                if tag_obj not in current_article.tags.all():
                    current_article.tags.add(tag_obj)
            current_article.save()

            return redirect('articles:article_detail', article_slug=current_article.slug)
    else:
        tags = ", ".join([tag.name for tag in current_article.tags.all() if tag])
        form = ArticleForm(initial={'title': current_article.title,
                                    'description': current_article.description,
                                    'content': current_article.content,
                                    'cover_image': current_article.cover_image,
                                    'tags': tags})

    return render(request, "articles/edit_article.html", context={"article_form": form})


@login_required
def article_delete(request, article_slug):
    get_object_or_404(Article, slug=article_slug).delete()
    return redirect("articles:article_list")


@login_required
def article_delete_comment(request, article_slug, comment_id):
    get_object_or_404(Comment, id=comment_id).delete()
    return redirect("articles:article_detail", article_slug=article_slug)


@login_required
def article_favorite(request, article_slug, favorite=True):
    current_user = request.user
    if favorite:
        current_user.favorite_article(article_slug=article_slug)
    else:
        current_user.unfavorite_article(article_slug=article_slug)
    return redirect('articles:article_detail', article_slug=article_slug)
