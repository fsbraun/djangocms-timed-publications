"""
Tests for TimedPublishingForm
"""

import pytest

from django.core.exceptions import ValidationError

from djangocms_timed_publishing.forms import TimedPublishingForm


@pytest.mark.django_db
class TestTimedPublishingForm:
    """Test cases for TimedPublishingForm"""

    def test_form_initialization(self):
        """Test form can be initialized"""
        form = TimedPublishingForm()
        assert 'visibility_start' in form.fields
        assert 'visibility_end' in form.fields

    def test_form_fields_are_optional(self):
        """Test that both fields are optional"""
        form = TimedPublishingForm(data={})
        assert form.is_valid()

    def test_form_field_labels(self):
        """Test form field labels"""
        form = TimedPublishingForm()
        assert form.fields['visibility_start'].label == "Visible after"
        assert form.fields['visibility_end'].label == "Visible until"

    def test_form_field_help_texts(self):
        """Test form field help texts"""
        form = TimedPublishingForm()
        assert form.fields['visibility_start'].help_text == "Leave empty for immediate public visibility"
        assert form.fields['visibility_end'].help_text == "Leave empty for unrestricted public visibility"

    def test_form_fields_not_required(self):
        """Test that form fields are not required"""
        form = TimedPublishingForm()
        assert form.fields['visibility_start'].required is False
        assert form.fields['visibility_end'].required is False

    def test_form_with_valid_future_dates(self, future_datetime, far_future_datetime):
        """Test form with valid future dates"""
        form = TimedPublishingForm(data={
            'visibility_start_0': future_datetime.date(),
            'visibility_start_1': future_datetime.time(),
            'visibility_end_0': far_future_datetime.date(),
            'visibility_end_1': far_future_datetime.time(),
        })
        assert form.is_valid()

    def test_clean_visibility_start_with_future_date(self, future_datetime):
        """Test clean_visibility_start with future date"""
        form = TimedPublishingForm(data={
            'visibility_start_0': future_datetime.date(),
            'visibility_start_1': future_datetime.time(),
        })
        form.is_valid()  # Trigger validation

        # Since clean_visibility_start uses timezone.make_aware,
        # we need to simulate the cleaned_data
        form.cleaned_data = {'visibility_start': future_datetime}
        result = form.clean_visibility_start()
        assert result is not None
        assert result.tzinfo is not None

    def test_clean_visibility_start_with_past_date_raises_error(self, past_datetime):
        """Test clean_visibility_start with past date raises ValidationError"""
        form = TimedPublishingForm()
        form.cleaned_data = {'visibility_start': past_datetime}

        with pytest.raises(ValidationError) as exc_info:
            form.clean_visibility_start()

        assert exc_info.value.code == "future"
        assert "must be in the future" in str(exc_info.value)

    def test_clean_visibility_end_with_future_date(self, future_datetime):
        """Test clean_visibility_end with future date"""
        form = TimedPublishingForm()
        form.cleaned_data = {'visibility_end': future_datetime}

        result = form.clean_visibility_end()
        assert result is not None
        assert result.tzinfo is not None

    def test_clean_visibility_end_with_past_date_raises_error(self, past_datetime):
        """Test clean_visibility_end with past date raises ValidationError"""
        form = TimedPublishingForm()
        form.cleaned_data = {'visibility_end': past_datetime}

        with pytest.raises(ValidationError) as exc_info:
            form.clean_visibility_end()

        assert exc_info.value.code == "future"
        assert "must be in the future" in str(exc_info.value)

    def test_clean_with_valid_time_interval(self, future_datetime, far_future_datetime):
        """Test clean method with valid time interval"""
        form = TimedPublishingForm()
        form.cleaned_data = {
            'visibility_start': future_datetime,
            'visibility_end': far_future_datetime
        }

        # Should not raise an exception
        form.clean()

    def test_clean_with_invalid_time_interval(self, future_datetime, past_datetime):
        """Test clean method with invalid time interval (start >= end)"""
        form = TimedPublishingForm()
        form.cleaned_data = {
            'visibility_start': future_datetime,
            'visibility_end': past_datetime
        }

        with pytest.raises(ValidationError) as exc_info:
            form.clean()

        assert exc_info.value.code == "time_interval"
        assert "must be after" in str(exc_info.value)

    def test_clean_with_equal_start_and_end_dates(self, future_datetime):
        """Test clean method with equal start and end dates"""
        form = TimedPublishingForm()
        form.cleaned_data = {
            'visibility_start': future_datetime,
            'visibility_end': future_datetime
        }

        with pytest.raises(ValidationError) as exc_info:
            form.clean()

        assert exc_info.value.code == "time_interval"

    def test_clean_with_only_start_date(self, future_datetime):
        """Test clean method with only start date"""
        form = TimedPublishingForm()
        form.cleaned_data = {
            'visibility_start': future_datetime,
            'visibility_end': None
        }

        # Should not raise an exception
        form.clean()

    def test_clean_with_only_end_date(self, future_datetime):
        """Test clean method with only end date"""
        form = TimedPublishingForm()
        form.cleaned_data = {
            'visibility_start': None,
            'visibility_end': future_datetime
        }

        # Should not raise an exception
        form.clean()

    def test_clean_with_no_dates(self):
        """Test clean method with no dates"""
        form = TimedPublishingForm()
        form.cleaned_data = {
            'visibility_start': None,
            'visibility_end': None
        }

        # Should not raise an exception
        form.clean()

    def test_form_widget_is_admin_split_datetime(self):
        """Test that the form uses AdminSplitDateTime widget"""
        form = TimedPublishingForm()
        from django.contrib.admin.widgets import AdminSplitDateTime

        assert isinstance(form.fields['visibility_start'].widget, AdminSplitDateTime)
        assert isinstance(form.fields['visibility_end'].widget, AdminSplitDateTime)
