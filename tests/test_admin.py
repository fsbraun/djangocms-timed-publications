from datetime import timedelta

import pytest

from cms.utils.urlutils import admin_reverse
from djangocms_versioning.constants import DRAFT, PUBLISHED

from djangocms_timed_publishing.models import TimedPublishingInterval


@pytest.mark.django_db
class TestAdmin:
    def test_publish_raises_error_if_not_get_or_post(self, client, admin_user, page_content):
        version = page_content.versions.first()
        url = admin_reverse("djangocms_versioning_pagecontentversion_publish", args=(version.pk,))
        client.login(username=admin_user.username, password='admin123')
        response = client.put(url)
        content = response.content.decode()

        assert content == "This view only supports GET or POST method."
        assert page_content.versions.first().state == DRAFT

    def test_publish_renders_form_on_get(self, client, admin_user, page_content):
        version = page_content.versions.first()
        url = admin_reverse("djangocms_versioning_pagecontentversion_publish", args=(version.pk,))
        client.login(username=admin_user.username, password='admin123')
        response = client.get(url)
        content = response.content.decode()

        assert "<form" in content
        assert "<b>Visible after</b>" in content
        assert "<b>Visible until</b>" in content

        assert page_content.versions.first().state == DRAFT  # Just showed the form, no state change

    def test_publish_renders_form_errors(self, client, admin_user, page_content):
        version = page_content.versions.first()
        url = admin_reverse("djangocms_versioning_pagecontentversion_publish", args=(version.pk,))
        client.login(username=admin_user.username, password='admin123')
        response = client.post(url, data={
            "visibility_start_1": "this is not a date"
        })
        content = response.content.decode()
        assert (
            '<ul class="errorlist" id="id_visibility_start_error"><li>Enter a valid time.</li></ul>' in content or
            '<ul class="errorlist"><li>Enter a valid time.</li></ul>' in content  # Django 4.2
        )
        assert page_content.versions.first().state == DRAFT  # Error, no state change


    def test_publish_must_affect_future(self, client, admin_user, page_content, past_datetime):

        version = page_content.versions.first()
        url = admin_reverse("djangocms_versioning_pagecontentversion_publish", args=(version.pk,))
        client.login(username=admin_user.username, password='admin123')
        data = {
            "visibility_start_0": past_datetime.date().isoformat(),
            "visibility_start_1": past_datetime.strftime("%H:%M"),
        }
        expected_error = "The date and time must be in the future."
        response = client.post(url, data=data)
        content = response.content.decode()

        assert page_content.versions.first().state == DRAFT  # Error, no state change

        assert (
            f'<ul class="errorlist" id="id_visibility_start_error"><li>{expected_error}</li></ul>' in content or
            f'<ul class="errorlist"><li>{expected_error}</li></ul>' in content  # Django 4.2
        )

    def test_publish_does_publish_without_form_data(self, client, admin_user, page_content):
        version = page_content.versions.first()
        url = admin_reverse("djangocms_versioning_pagecontentversion_publish", args=(version.pk,))
        client.login(username=admin_user.username, password='admin123')
        client.post(url)

        assert page_content.versions.first().state == PUBLISHED

    def test_publish_does_respect_form_data(self, client, admin_user, page_content, future_datetime, far_future_datetime):
        version = page_content.versions.first()
        url = admin_reverse("djangocms_versioning_pagecontentversion_publish", args=(version.pk,))
        client.login(username=admin_user.username, password='admin123')
        data = {
            "visibility_start_0": future_datetime.date().isoformat(),
            "visibility_start_1": future_datetime.strftime("%H:%M"),
            "visibility_end_0": far_future_datetime.date().isoformat(),
            "visibility_end_1": far_future_datetime.strftime("%H:%M"),
        }
        client.post(url, data=data)

        version = page_content.versions.first()
        assert version.state == PUBLISHED
        assert hasattr(version, "visibility")

    def test_publish_gracefully_handles_id_mismatch(self, client, admin_user, page_content, future_datetime, far_future_datetime):
        version = page_content.versions.first()
        url = admin_reverse("djangocms_versioning_pagecontentversion_publish", args=(-version.pk,))
        client.login(username=admin_user.username, password='admin123')
        data = {
            "visibility_start_0": future_datetime.date().isoformat(),
            "visibility_start_1": future_datetime.strftime("%H:%M"),
            "visibility_end_0": far_future_datetime.date().isoformat(),
            "visibility_end_1": far_future_datetime.strftime("%H:%M"),
        }
        response = client.post(url, data=data)

        assert response.status_code == 302 or response.status_code == 301
        assert response.url == "/admin/"

        version = page_content.versions.first()
        assert version.state == DRAFT  # Should not change state due to ID mismatch
        assert not hasattr(version, "visibility")

    def test_changelist_view_state(self, client, admin_user, page_content, past_datetime, future_datetime):
        version = page_content.versions.first()
        version.publish(admin_user)
        url = admin_reverse("djangocms_versioning_pagecontentversion_changelist") + f"?page={page_content.page.pk}"
        interval = TimedPublishingInterval.objects.create(
            version=version,
            start=future_datetime,
            end=future_datetime + timedelta(days=1)
        )

        client.login(username=admin_user.username, password='admin123')
        response = client.get(url)
        content = response.content.decode()

        assert "Pending" in content

        interval.start = past_datetime - timedelta(days=1)
        interval.end = past_datetime
        interval.save()

        response = client.get(url)
        content = response.content.decode()

        assert "Expired" in content

