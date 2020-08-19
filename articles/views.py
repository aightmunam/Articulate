from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage,\
    PageNotAnInteger
from django.conf import settings
from django.contrib.postgres.search import SearchVector

from .models import Article, Tag
from .forms import ArticleForm, CommentForm, SearchForm

# Create your views here.
def aritcle_index(request):
    return render(request, 'pages/home.html', context={})

def article_list(request, tag_slug=None):
    object_list = Article.objects.all().order_by('-created_at')
    tag = None
    search_form = SearchForm()
    query = None

    if 'query' in request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            object_list = Article.objects.annotate(search=SearchVector('title', 'description', 'content'),).filter(search=query)

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 5)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    return render(request, "articles/list.html", context={"page": page,"articles": articles, "tag": tag, "search_form":search_form, "query": query})

def article_detail(request, article_id, article_slug):
    article = get_object_or_404(Article, id=article_id, slug=article_slug)

    article_tags = article.tags.values_list('id', flat=True)
    similar_articles = Article.objects.filter(tags__in=article_tags).exclude(id=article.id)
    similar_articles = similar_articles.annotate(same_tags=Count('tags')).order_by('-same_tags', '-created_at')

    comments = article.comments.all()

    paginator = Paginator(comments, 5)
    page = request.GET.get('page')
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)

    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.author = request.user
            new_comment.save()
    else:
        comment_form = CommentForm()

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
            obj = form.save(commit=False)
            obj.author = request.user
            obj.save()
            redirect('articles:article_list')
    else:
        form = ArticleForm()

    return render(request, "articles/create_new.html", context={"article_form": form})
