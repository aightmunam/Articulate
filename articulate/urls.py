"""
articulate URL Configuration
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from articles.api.views import api_root
from articles.views import article_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', article_list, name='index'),
    path('', include('social_django.urls', namespace='social')),
    path('profiles/', include('profiles.urls', namespace='profiles')),
    path('articles/', include('articles.urls', namespace='articles')),
    path('api/', api_root, name='api-root'),
    path('api/articles/', include('articles.api.urls', namespace='api_articles')),
    path('api/profiles/', include('profiles.api.urls', namespace='api_profiles'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
