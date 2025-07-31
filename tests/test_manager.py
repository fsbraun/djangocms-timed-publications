from datetime import timedelta

import pytest

from cms.models import PageContent

from djangocms_timed_publishing.models import TimedPublishingInterval


@pytest.mark.django_db
class TestManager:
    """Test cases for manager functionality"""

    def test_unpublished_never_visible(self, page_content, past_datetime):
        """Test manager can be initialized"""

        assert not PageContent.objects.filter(pk=page_content.pk).exists()

        version = page_content.versions.first()
        TimedPublishingInterval.objects.create(
            version=version,
            start=past_datetime,
        )
        assert not PageContent.objects.filter(pk=page_content.pk).exists()

    def test_published_visible(self, page_content, admin_user, past_datetime, future_datetime):
        """Test manager can be initialized"""
        version = page_content.versions.first()
        version.publish(admin_user)

        assert PageContent.objects.filter(pk=page_content.pk).exists()

    def test_published_visible_if_interval_starts_in_past(self, page_content, admin_user, past_datetime, future_datetime):
        version = page_content.versions.first()
        version.publish(admin_user)

        interval = TimedPublishingInterval.objects.create(
            version=version,
            start=past_datetime,
        )
        assert PageContent.objects.filter(pk=page_content.pk).exists()

        interval.start = past_datetime - timedelta(days=1)
        interval.end = future_datetime
        interval.save()

        assert PageContent.objects.filter(pk=page_content.pk).exists()

    def test_published_not_visible_if_interval_starts_in_past(self, page_content, admin_user, past_datetime):
        version = page_content.versions.first()
        version.publish(admin_user)

        interval = TimedPublishingInterval.objects.create(
            version=version,
            start=past_datetime - timedelta(days=1),
            end=past_datetime
        )

        assert not PageContent.objects.filter(pk=page_content.pk).exists()

        interval.start = None
        interval.end = past_datetime
        interval.save()

        assert not PageContent.objects.filter(pk=page_content.pk).exists()


