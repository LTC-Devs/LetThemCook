from django.contrib import admin

from .models import UserFeaturePref, UserSettings


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ("user", "default_servings")
    search_fields = ("user__username",)
    autocomplete_fields = ("user",)


@admin.register(UserFeaturePref)
class UserFeaturePrefAdmin(admin.ModelAdmin):
    list_display = ("user", "feature", "level")
    list_filter = ("level",)
    search_fields = ("user__username", "feature__name")
    autocomplete_fields = ("user", "feature")
