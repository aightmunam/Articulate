"""
App config for articles app
"""
from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    """
    Config for Article
    """
    name = 'articles'

    def ready(self):
        from . import receivers
