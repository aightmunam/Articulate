from django.apps import AppConfig
from .signals import tag_click
# from .receivers import update_tag_click_status

class ArticlesConfig(AppConfig):
    name = 'articles'

    def ready(self):
        from . import receivers
        # tag_click.connect(update_tag_click_status, sender='articles.Tag')
