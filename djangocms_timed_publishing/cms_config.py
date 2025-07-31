from urllib.parse import unquote

from django.contrib import admin
from django.db import models
from django.http import HttpResponseNotAllowed
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from cms.app_base import CMSAppConfig
from djangocms_versioning import constants
from djangocms_versioning.admin import VersionAdmin
from djangocms_versioning.cms_toolbars import VersioningToolbar
from djangocms_versioning.managers import PublishedContentManagerMixin
from djangocms_versioning.models import Version

from .cms_toolbars import _get_published_page_version
from .forms import TimedPublishingForm
from .models import TimedPublishingInterval

PENDING = _("Pending")
EXPIRED = _("Expired")


def patch_publish_view(original_view):
    """
    Patch the publish view to handle time restrictions.
    This function is used to ensure that the publish view
    correctly processes time-restricted visibility.
    """
    def patched_view(self, request, object_id, *args, **kwargs):
        if request.method not in ("GET", "POST"):
            return HttpResponseNotAllowed(
                ["GET", "POST"], _("This view only supports GET or POST method.")
            )
        form = TimedPublishingForm(request.POST) if request.method == "POST" else TimedPublishingForm()
        if request.method == "GET" or not form.is_valid():
            return render(
                request,
                template_name="djangocms_versioning/admin/timed_publishing.html",
                context={"form": form, "errors": request.method != "GET" and not form.is_valid()},
            )

        visibility_start = form.cleaned_data["visibility_start"]
        visibility_end = form.cleaned_data["visibility_end"]

        if visibility_start or visibility_end:
            # Check version exists
            version = self.get_object(request, unquote(object_id))
            if version is None:
                return self._get_obj_does_not_exist_redirect(
                    request, self.model._meta, object_id
                )
            else:
                TimedPublishingInterval.objects.update_or_create(
                    version=version,
                    defaults={
                        'start': visibility_start,
                        'end': visibility_end,
                    }
                )

        return original_view(self, request, object_id, *args, **kwargs)
    return patched_view


def patch_short_name(self):
    state = dict(constants.VERSION_STATES)[self.state]
    if self.state == constants.PUBLISHED and hasattr(self, 'visibility'):
        if self.visibility.start and self.visibility.start > timezone.now():
            state = PENDING
        elif self.visibility.end and self.visibility.end < timezone.now():
            state = EXPIRED
    return _("Version #{number} ({state})").format(
        number=self.number, state=state
    )


def patch_get_queryset(original_get_queryset: callable) -> callable:
    """
    Patch the get_queryset method to filter by visibility.
    This function ensures that only versions with valid visibility
    are returned in the queryset.
    """
    def patched_get_queryset(self):
        queryset = original_get_queryset(self)
        if not self.versioning_enabled:  # pragma: no cover
            # If versioning is not enabled, return the original queryset
            return queryset
        now = timezone.now()
        return queryset.filter(
            models.Q(versions__visibility__start=None) | models.Q(versions__visibility__start__lt=now),
            models.Q(versions__visibility__end=None) | models.Q(versions__visibility__end__gt=now),
        )

    return patched_get_queryset

@admin.display(description=_("State"), ordering="state")
def get_state(self: admin.ModelAdmin, obj: Version) -> str:
    """
    Get the state of the version, considering visibility.
    This function is used to determine the state of a version
    in the admin interface, taking into account time restrictions.
    """
    if obj.state == constants.PUBLISHED and hasattr(obj, 'visibility'):
        if obj.visibility.start and obj.visibility.start > timezone.now():
            return PENDING
        elif obj.visibility.end and obj.visibility.end < timezone.now():
            return EXPIRED
    return dict(constants.VERSION_STATES)[obj.state]


class TimedPublishingConfig(CMSAppConfig):
    VersionAdmin.publish_view = patch_publish_view(VersionAdmin.publish_view)
    VersionAdmin.get_state = get_state
    VersionAdmin.list_display = ["get_state" if item == "state" else item for item in VersionAdmin.list_display]
    Version.short_name = patch_short_name
    PublishedContentManagerMixin.get_queryset = patch_get_queryset(
        PublishedContentManagerMixin.get_queryset
    )
    VersioningToolbar._get_published_page_version = _get_published_page_version
