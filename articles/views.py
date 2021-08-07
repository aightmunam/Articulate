"""
Views for the articles app
"""
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (CreateView, DeleteView, FormView, ListView,
                                  UpdateView)
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormMixin

from .forms import ArticleForm, CommentForm, SearchForm
from .helpers import (
    get_articles_liked_and_authored_by_followed_profiles,
    get_articles_tagged_by_given_tag,
    get_most_similar_articles_based_on_trigram_similarity,
    get_top_n_most_popular_tags
)
from .models import Article, Comment, Tag


class ArticleListView(FormMixin, ListView):
    """
    View to handle all the data of the index page
    """
    model = Article
    template_name = 'articles/list.html'
    paginate_by = 3
    form_class = SearchForm
    context_object_name = 'articles'

    def get_queryset(self):
        feed_articles = self.get_feed_articles()

        if 'query' in self.request.GET:
            search_form = SearchForm(self.request.GET)
            if search_form.is_valid():
                search_query = search_form.cleaned_data['query']
                feed_articles = get_most_similar_articles_based_on_trigram_similarity(search_query)

        tag_slug_query = self.kwargs.get('tag_slug')
        if tag_slug_query:
            feed_articles = get_articles_tagged_by_given_tag(feed_articles, tag_slug_query)

        return feed_articles

    def get_context_data(self, **kwargs):
        context = super(ArticleListView, self).get_context_data(**kwargs)
        context.update({
            'popular_tags': get_top_n_most_popular_tags(self.get_queryset(), 5),
            'search_form': self.get_form(),
            'query': self.request.GET.get('query'),
            'local': self.kwargs.get('local'),
            'tag': self.kwargs.get('tag_slug')
        })

        return context

    def get_feed_articles(self):
        """
        Gets the user's local feed if there is a authenticated user otherwise returns the
        feed common to all users.

        Returns:
            QuerySet: A queryset containing articles to be shown in the newsfeed
        """
        if self.kwargs.get('local'):
            if self.request.user.is_authenticated:
                return get_articles_liked_and_authored_by_followed_profiles(self.request.user)

        return Article.objects.all().order_by('-created_at').select_related('author').prefetch_related('tags')


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
