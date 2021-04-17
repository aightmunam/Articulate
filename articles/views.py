"""
Views for the articles app
"""
import collections

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, FormView, UpdateView
from django.views.generic.detail import DetailView, SingleObjectMixin

from .forms import ArticleForm, CommentForm, SearchForm
from .models import Article, Comment, Tag
from .signals import tag_click


def article_list(request, tag_slug=None, local=False):
    """
    Lists all the articles, add query functionality
    """
    feed_articles = None
    if local:
        if request.user.is_authenticated:
            current_user_following = request.user.get_followed_profiles()
            local_feed_articles = []

            following_users_authored_articles = [followed_user.get_authored_articles() for followed_user in
                                                 current_user_following if followed_user]
            if following_users_authored_articles:
                local_feed_articles = following_users_authored_articles[0]
                for followed_user_article_qs in following_users_authored_articles:
                    local_feed_articles = (local_feed_articles | followed_user_article_qs)

            following_users_starred_articles = [followed_user.get_favorite_articles() for followed_user in
                                                current_user_following if followed_user]
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
                feed_articles = Article.objects.annotate(similarity=TrigramSimilarity('title', query), ).filter(
                    similarity__gt=0.1).order_by('-similarity')

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

    return render(request, 'articles/list.html', {
        'page': page, 'articles': articles, 'tag': tag, 'search_form': search_form, 'query': query, 'local': local,
        'popular_tags': top_five_most_popular_tags
    })


class ArticleDetailView(View):
    """
    View to handle the Article detail page
    """

    def get(self, request, *args, **kwargs):
        view = ArticleDetailDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ArticleDetailFormView.as_view()
        return view(request, *args, **kwargs)


class ArticleDetailFormView(LoginRequiredMixin, SingleObjectMixin, FormView):
    """
    Article detail view to handle post requests for embedded form
    """

    form_class = CommentForm
    model = Article
    slug_url_kwarg = 'article_slug'
    template_name = 'articles/detail.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(request=self.request, article=self.object)
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super(ArticleDetailFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse('articles:article_detail', kwargs={'article_slug': self.object.slug})


class ArticleDetailDisplay(DetailView):
    """
    View for the detail page of Article
    """

    model = Article
    slug_url_kwarg = 'article_slug'
    template_name = 'articles/detail.html'

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailDisplay, self).get_context_data()
        comments = self.object.get_all_comments()
        paginator = Paginator(comments, 5)

        page = self.request.GET.get('page')
        try:
            comments = paginator.page(page)
        except PageNotAnInteger:
            comments = paginator.page(1)
        except EmptyPage:
            comments = paginator.page(paginator.num_pages)

        context.update({
            'comment_form': CommentForm(),
            'page': page,
            'comments': comments,
        })

        return context


class ArticleCreateView(LoginRequiredMixin, CreateView):
    """
    View to create a new article
    """

    form_class = ArticleForm
    model = Article
    slug_url_kwarg = 'article_slug'
    template_name_suffix = '_form'

    def get_form_kwargs(self, *args, **kwargs):
        """
        Add request object to the form
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View to update an Article
    """

    form_class = ArticleForm
    model = Article
    slug_url_kwarg = 'article_slug'
    template_name_suffix = '_form'

    def test_func(self):
        """
        Only allow deletion if the authenticated user is the author of the article
        """
        article_slug = self.kwargs.get('article_slug')
        return Article.objects.filter(slug=article_slug, author=self.request.user).exists()

    def get_form_kwargs(self, *args, **kwargs):
        """
        Add request object to the form
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        """
        Send the context data to the template for rendering.

        Returns:
            HttpResponse object.
        """
        self.object = self.get_object()
        tags = ", ".join([tag.name for tag in self.object.tags.all() if tag])

        form = self.form_class(initial={'title': self.object.title,
                                        'description': self.object.description,
                                        'content': self.object.content,
                                        'cover_image': self.object.cover_image,
                                        'tags': tags})

        return render(request, 'articles/article_form.html', {'form': form})


class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View to delete an Article
    """

    model = Article
    slug_url_kwarg = 'article_slug'
    success_url = reverse_lazy('articles:article_list')
    template_name = 'components/confirm_delete.html'

    def test_func(self):
        """
        Only allow deletion if the authenticated user is the author of the article
        """
        article_slug = self.kwargs.get('article_slug')
        return Article.objects.filter(slug=article_slug, author=self.request.user).exists()


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View to delete a Comment on an Article
    """

    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'components/confirm_delete.html'

    def test_func(self):
        """
        Only allow delete if the logged in user is either the author of the comment or the article
        """
        comment_id = self.kwargs.get('comment_id')
        article_slug = self.kwargs.get('article_slug')

        is_comment_author = Comment.objects.filter(id=comment_id, author=self.request.user).exists()
        is_article_author = Article.objects.filter(slug=article_slug, author=self.request.user).exists()

        return is_article_author or is_comment_author

    def get_success_url(self):
        article_slug = self.kwargs.get('article_slug')
        return reverse_lazy('articles:article_detail', kwargs={'article_slug': article_slug})


class ArticleRateView(LoginRequiredMixin, SingleObjectMixin, View):
    """
    View that handles the favourite and un-favourite functionality of an article
    """

    model = Article

    def get(self, request, slug, rate):  # pylint: disable=unused-argument
        self.object = self.get_object()
        self.request.user.toggle_article_favourite(slug)

        return redirect('articles:article_detail', article_slug=slug)
