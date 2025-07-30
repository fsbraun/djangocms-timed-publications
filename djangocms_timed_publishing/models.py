from django.db import models
from django.utils.translation import gettext_lazy as _



class TimedPublishingInterval(models.Model):
    version = models.OneToOneField(
        'djangocms_versioning.Version',
        on_delete=models.CASCADE,
        related_name='visibility',
    )

    start = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        verbose_name=_("visible after"),
        help_text=_("Leave empty for immediate public visibility"),
    )

    end = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        verbose_name=_("visible until"),
        help_text=_("Leave empty for unrestricted public visibility"),
    )
