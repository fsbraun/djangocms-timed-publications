from datetime import timedelta

import pytest

from cms.toolbar.utils import get_object_edit_url, get_object_preview_url
from cms.utils.urlutils import admin_reverse

from djangocms_timed_publishing.models import TimedPublishingInterval


@pytest.mark.django_db
class TestToolbar:
    def test_toolbar_offers_timed_publishing(self, client, admin_user, page_content):
        """Test that the toolbar initializes correctly for an admin user"""
        client.login(username=admin_user.username, password='admin123')
        response = client.get(get_object_edit_url(page_content))
        content = response.content.decode()

        assert "Version" in content

        assert "Publish with time limits..." in content

    def test_toolbar_does_not_offer_timed_publishing_in_preview(self, client, admin_user, page_content):
        """Test that the toolbar initializes correctly for an admin user"""
        client.login(username=admin_user.username, password='admin123')
        response = client.get(get_object_preview_url(page_content))
        content = response.content.decode()

        assert "Version" in content

        assert "Publish with time limits..." not in content

    def test_toolbar_contains_timed_publishing_info(self, client, admin_user, page_content, past_datetime, future_datetime):
        """Test that the toolbar contains timed publishing information"""
        version = page_content.versions.first()
        version.publish(admin_user)

        interval = TimedPublishingInterval.objects.create(
            version=version,
            start=past_datetime,
            end=future_datetime
        )

        client.login(username=admin_user.username, password='admin123')
        response = client.get(get_object_preview_url(page_content))
        content = response.content.decode()

        assert "Visible since" in content
        assert "Visible until" in content

        interval.start = future_datetime
        interval.end = future_datetime + timedelta(days=1)
        interval.save()

        response = client.get(get_object_preview_url(page_content))
        content = response.content.decode()

        assert f"Version #{version.pk} (Pending)" in content
        assert "Visible after" in content
        assert "Visible until" in content

        interval.start = past_datetime - timedelta(days=1)
        interval.end = past_datetime
        interval.save()

        response = client.get(get_object_preview_url(page_content))
        content = response.content.decode()

        assert f"Version #{version.pk} (Expired)" in content
        assert "Visible since" in content
        assert "Visible until" in content

    @pytest.mark.django_db
    @pytest.mark.parametrize("timed_publishing_button", [True, False])
    def test_toolbar_respects_always_timed_publishing_setting(
        self, client, admin_user, page_content, settings, timed_publishing_button
    ):
        """
        Test that the toolbar offers timed publishing based on the
        DJANGOCMS_ALWAYS_TIMED_PUBLISHING setting.
        """
        settings.DJANGOCMS_TIMED_PUBLISHING_BUTTON = timed_publishing_button
        client.login(username=admin_user.username, password='admin123')
        response = client.get(get_object_edit_url(page_content))
        content = response.content.decode()

        if timed_publishing_button:
            version = page_content.versions.first()
            version = version.convert_to_proxy()

            url = admin_reverse(
                f"{version._meta.app_label}_{version._meta.model_name}_publish",
                args=(page_content.pk,)
            )
            timed_button = (
                f'<a href="{url}" class="cms-btn cms-btn-action" data-rel="modal" data-on-close="REFRESH_PAGE">Publish</a>'
            )
            assert "Publish with time limits..." not in content
            assert timed_button in content
        else:
            assert "Publish with time limits..." in content  # fallback: feature is always available unless logic changes

