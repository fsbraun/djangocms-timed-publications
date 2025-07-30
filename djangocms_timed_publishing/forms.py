from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TimedPublishingForm(forms.Form):
    visibility_start = forms.SplitDateTimeField(
        required=False,
        label=_("Visible after"),
        help_text=_("Leave empty for immediate public visibility"),
        widget=AdminSplitDateTime,
    )

    visibility_end = forms.SplitDateTimeField(
        required=False,
        label=_("Visible until"),
        help_text=_("Leave empty for unrestricted public visibility"),
        widget=AdminSplitDateTime,
    )

    def clean_visibility_start(self):
        visibility_start = self.cleaned_data["visibility_start"]

        if visibility_start and visibility_start < timezone.now():
            raise ValidationError(
                _("The date and time must be in the future."), code="future"
            )
        return visibility_start

    def clean_visibility_end(self):
        visibility_end = self.cleaned_data["visibility_end"]
        if visibility_end and visibility_end < timezone.now():
            raise ValidationError(
                _("The date and time must be in the future."), code="future"
            )
        return visibility_end

    def clean(self):
        if self.cleaned_data.get("visibility_start") and self.cleaned_data.get("visibility_end"):
            if self.cleaned_data["visibility_start"] >= self.cleaned_data["visibility_end"]:
                raise ValidationError(
                    _("The time until the content is visible must be after the time "
                      "the content becomes visible."), code="time_interval")
