from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage,\
    PageNotAnInteger
from django.conf import settings
from django.contrib.postgres.search import TrigramSimilarity

from .models import Article, Tag, Comment
from .forms import ArticleForm, CommentForm, SearchForm

# Create your views here.
def aritcle_index(request):
    return redirect("articles:article_list")

def article_list(request, tag_slug=None):
    object_list = Article.objects.all().order_by('-created_at')
    tags = Tag.objects.all().order_by('-created_at')
    search_form = SearchForm()
    tag = None
    query = None
    print(query)

    if 'query' in request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            object_list = Article.objects.annotate(similarity=TrigramSimilarity('title', query),).filter(similarity__gt=0.1).order_by('-similarity')

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 4)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    return render(request, "articles/list.html", context={"page": page,
                                                          "articles": articles,
                                                          "recent_tags":tags,
                                                          "tag": tag,
                                                          "search_form":search_form,
                                                          "query": query})

def article_detail(request, article_slug):
    article = get_object_or_404(Article, slug=article_slug)

    article_tags = article.tags.values_list('id', flat=True)
    similar_articles = Article.objects.filter(tags__in=article_tags).exclude(id=article.id)
    similar_articles = similar_articles.annotate(same_tags=Count('tags')).order_by('-same_tags', '-created_at')

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

    comments = article.comments.all().order_by('-created_at')
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
                                                            "comment_form": comment_form,
                                                            "similar_articles": similar_articles})

def article_create_new(request):
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)

    if request.method == 'POST':
        form = ArticleForm(data=request.POST)
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


def article_edit(request, article_slug):
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)

    current_article =  get_object_or_404(Article, slug=article_slug)
    if request.method == 'POST':
        form = ArticleForm(data=request.POST, files=request.FILES or None, instance=current_article)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            current_article.title = cleaned_data['title']
            current_article.description = cleaned_data['description']
            current_article.content = cleaned_data['content']
            print(cleaned_data["cover_image"])
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

def article_delete(request, article_slug):
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)

    Article.objects.filter(slug=article_slug).delete()
    return redirect("articles:article_list")


def article_delete_comment(request, article_slug, comment_id):
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)

    Comment.objects.filter(id=comment_id).delete()
    return redirect("articles:article_detail", article_slug=article_slug)


def article_favorite(request, article_slug):
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)

    current_user = request.user
    if current_user.starred_articles.filter(slug=article_slug).exists():
        current_user.starred_articles.remove(current_user.starred_articles.get(slug=article_slug))
    else:
        current_user.starred_articles.add(Article.objects.get(slug=article_slug))


    return redirect('articles:article_detail', article_slug=article_slug)

