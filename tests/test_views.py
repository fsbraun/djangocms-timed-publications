import pytest

from cms.utils.urlutils import admin_reverse


@pytest.mark.django_db
class TestToolbar:
    def test_publish_raises_error_if_not_get_or_post(self, client, admin_user, page_content):
        version = page_content.versions.first()
        url = admin_reverse("djangocms_versioning_pagecontentversion_publish", args=(version.pk,))
        client.login(username=admin_user.username, password='admin123')
        response = client.put(url)
        content = response.content.decode()

        assert content == "This view only supports GET or POST method."

    def test_publish_renders_form_on_get(self, client, admin_user, page_content):
        version = page_content.versions.first()
        url = admin_reverse("djangocms_versioning_pagecontentversion_publish", args=(version.pk,))
        client.login(username=admin_user.username, password='admin123')
        response = client.get(url)
        content = response.content.decode()

        assert "<form" in content
        assert "<b>Visible after</b>" in content
        assert "<b>Visible until</b>" in content
        
    def test_publish_renders_form_errors(self, client, admin_user, page_content):
        version = page_content.versions.first()
        url = admin_reverse("djangocms_versioning_pagecontentversion_publish", args=(version.pk,))
        client.login(username=admin_user.username, password='admin123')
        response = client.post(url, data={
            "visibility_start_1": "this is not a date"
        })
        content = response.content.decode()
        assert '<ul class="errorlist" id="id_visibility_start_error"><li>Enter a valid time.</li></ul>' in content

    def test_publish_does_publish_without_form_data(self, client, admin_user, page_content):
        from djangocms_versioning.constants import PUBLISHED
        
        version = page_content.versions.first()
        url = admin_reverse("djangocms_versioning_pagecontentversion_publish", args=(version.pk,))
        client.login(username=admin_user.username, password='admin123')
        client.post(url)

        assert page_content.versions.first().state == PUBLISHED
