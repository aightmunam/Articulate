from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.core.paginator import Paginator, EmptyPage,\
    PageNotAnInteger
from django.conf import settings

from .models import Article, Tag
from .forms import ArticleForm, CommentForm

# Create your views here.
def aritcle_index(request):
    return render(request, 'pages/home.html', context={})

def article_list(request, tag_slug=None):
    object_list = Article.objects.all().order_by('-created_at')
    tag = None
    
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
    paginator = Paginator(object_list, 3)  # 3 posts in each page
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        articles = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        articles = paginator.page(paginator.num_pages)

    return render(request, "articles/list.html", context={"page": page,"articles": articles})

def article_detail(request, article_id, article_slug):
    article = get_object_or_404(Article, id=article_id, slug=article_slug)
    comments = article.comments.all()
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
                                                            "comments": comments,
                                                            "new_comment": new_comment,
                                                            "comment_form": comment_form})

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