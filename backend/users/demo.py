"""Shared, single-user demo access for the local LTC prototype only."""
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied


def demo_user():
    if not settings.LTC_DEMO_MODE:
        raise PermissionDenied('Tryb demo jest wyłączony (LTC_DEMO_MODE=0).')
    user, created = get_user_model().objects.get_or_create(username='ltc-demo')
    if created:
        user.set_unusable_password()
        user.save(update_fields=['password'])
    return user
