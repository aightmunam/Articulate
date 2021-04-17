"""articulate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from articles.api.views import api_root
from articles.views import aritcle_index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', aritcle_index, name='index'),
    path('', include('social_django.urls', namespace='social')),
    path('profiles/', include('profiles.urls', namespace='profiles')),
    path('articles/', include('articles.urls', namespace='articles')),
    path('api/', api_root, name='api-root'),
    path('api/articles/', include('articles.api.urls', namespace='api_articles')),
    path('api/profiles/', include('profiles.api.urls', namespace='api_profiles'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
