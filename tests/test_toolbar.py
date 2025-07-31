from datetime import timedelta

import pytest

from cms.toolbar.utils import get_object_edit_url, get_object_preview_url

from djangocms_timed_publishing.models import TimedPublishingInterval


@pytest.fixture
def page(admin_user):
    """Create a test page"""
    from cms.api import create_page

    return create_page(
        title='Test Page',
        template='template.html',
        language='en',
        slug='test-page',
        created_by=admin_user,
        in_navigation=True
    )


@pytest.fixture
def page_content(page):
    """Create a test page content"""
    return page.pagecontent_set(manager="admin_manager").first()


@pytest.fixture
def object_edit_endpoint_content(client, page_content, admin_user):
    """Get the edit URL for a page content"""
    client.login(username=admin_user.username, password='admin123')
    response = client.get(get_object_edit_url(page_content))
    return response.content.decode()


@pytest.mark.django_db
class TestToolbar:
    def test_toolbar_offers_timed_publishing(self, client, admin_user, page_content):
        """Test that the toolbar initializes correctly for an admin user"""
        client.login(username=admin_user.username, password='admin123')
        response = client.get(get_object_edit_url(page_content))
        content = response.content.decode()

        assert "Version" in content

        assert "Publish with time limits..." in content

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
