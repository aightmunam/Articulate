from django.dispatch import receiver

from .signals import tag_click


@receiver(tag_click)
def update_tag_click_status(sender, tag, profile, **kwargs):
    if tag:
        tag.increase_click_count()
        if profile:
            tag.add_profile_to_clicked(profile)
