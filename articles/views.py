from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse

from .models import Article

# Create your views here.
def aritcle_index(request):
    return render(request, 'pages/home.html', context={})

def article_list(request):
    articles = Article.objects.all()
    if not articles:
        raise Http404
    return render(request, "articles/list.html", context={"articles": articles})

def article_detail(request, article_id, article_slug):
    article = get_object_or_404(Article, id=article_id, slug=article_slug)
    comments = article.comments.all()
    return render(request, "articles/detail.html", context={"article": article, 
                                                            "comments": comments})
    # return HttpResponse("<h1>This is article {} - {} - {} by author {}</h1>".format(obj.id, obj.title, obj.description, obj.author))