from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.core.paginator import Paginator, EmptyPage,\
    PageNotAnInteger

from .models import Article

# Create your views here.
def aritcle_index(request):
    return render(request, 'pages/home.html', context={})

def article_list(request):
    object_list = Article.objects.all().order_by('-created_at')
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

    if not articles:
        raise Http404
    return render(request, "articles/list.html", context={"page": page,"articles": articles})

def article_detail(request, article_id, article_slug):
    article = get_object_or_404(Article, id=article_id, slug=article_slug)
    comments = article.comments.all()
    return render(request, "articles/detail.html", context={"article": article, 
                                                            "comments": comments})
    # return HttpResponse("<h1>This is article {} - {} - {} by author {}</h1>".format(obj.id, obj.title, obj.description, obj.author))