from django.db.models import Q
from django.utils import timezone

from djangocms_versioning.constants import PUBLISHED


def get_queryset(self):
    """Limit query to published content
    """
    queryset = super().get_queryset()
    if not self.versioning_enabled:
        return queryset
    now = timezone.now()
    return queryset.filter(
        Q(versions__visibility__start=None) | Q(versions__visibility__start__lt=now),
        Q(versions__visibility__end=None) | Q(versions__visibility__end__gt=now),
        versions__state=PUBLISHED,
    )

