"""
Tests for TimedPublishingInterval model
"""

import pytest

from djangocms_timed_publishing.models import TimedPublishingInterval


@pytest.mark.django_db
class TestTimedPublishingInterval:
    """Test cases for TimedPublishingInterval model"""

    def test_model_creation(self):
        """Test basic model instance creation"""
        interval = TimedPublishingInterval()
        assert interval.start is None
        assert interval.end is None
        assert interval.version_id is None

    def test_model_fields(self):
        """Test model field configuration"""
        fields = TimedPublishingInterval._meta.get_fields()
        field_names = [field.name for field in fields]

        assert 'version' in field_names
        assert 'start' in field_names
        assert 'end' in field_names

    def test_start_field_properties(self):
        """Test start field properties"""
        start_field = TimedPublishingInterval._meta.get_field('start')
        assert start_field.null is True
        assert start_field.blank is True
        assert start_field.default is None

    def test_end_field_properties(self):
        """Test end field properties"""
        end_field = TimedPublishingInterval._meta.get_field('end')
        assert end_field.null is True
        assert end_field.blank is True
        assert end_field.default is None

    def test_version_field_relationship(self):
        """Test version field is OneToOneField"""
        version_field = TimedPublishingInterval._meta.get_field('version')
        assert version_field.one_to_one is True
        assert version_field.related_model.__name__ == 'Version'

    def test_str_representation(self):
        """Test string representation of model"""
        interval = TimedPublishingInterval()
        # Since there's no explicit __str__ method, it should use default
        str_repr = str(interval)
        assert 'TimedPublishingInterval' in str_repr

    def test_model_verbose_names(self):
        """Test field verbose names"""
        start_field = TimedPublishingInterval._meta.get_field('start')
        end_field = TimedPublishingInterval._meta.get_field('end')

        assert start_field.verbose_name == "visible after"
        assert end_field.verbose_name == "visible until"

    def test_model_help_texts(self):
        """Test field help texts"""
        start_field = TimedPublishingInterval._meta.get_field('start')
        end_field = TimedPublishingInterval._meta.get_field('end')

        assert start_field.help_text == "Leave empty for immediate public visibility"
        assert end_field.help_text == "Leave empty for unrestricted public visibility"

    def test_with_future_dates(self, future_datetime, far_future_datetime):
        """Test model with future start and end dates"""
        interval = TimedPublishingInterval(
            start=future_datetime,
            end=far_future_datetime
        )
        assert interval.start == future_datetime
        assert interval.end == far_future_datetime

    def test_with_past_dates(self, past_datetime, far_past_datetime):
        """Test model with past start and end dates"""
        interval = TimedPublishingInterval(
            start=far_past_datetime,
            end=past_datetime
        )
        assert interval.start == far_past_datetime
        assert interval.end == past_datetime

    def test_with_only_start_date(self, future_datetime):
        """Test model with only start date set"""
        interval = TimedPublishingInterval(start=future_datetime)
        assert interval.start == future_datetime
        assert interval.end is None

    def test_with_only_end_date(self, future_datetime):
        """Test model with only end date set"""
        interval = TimedPublishingInterval(end=future_datetime)
        assert interval.start is None
        assert interval.end == future_datetime
