from django.dispatch import Signal

tag_click = Signal(providing_args=["tag", "profile"])