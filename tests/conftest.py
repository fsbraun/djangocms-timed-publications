"""
Test configuration and fixtures for djangocms-timed-publishing tests
"""
from datetime import timedelta

import pytest

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.utils import timezone

User = get_user_model()


@pytest.fixture
def user():
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user():
    """Create an admin user"""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )


@pytest.fixture
def request_factory():
    """Django RequestFactory instance"""
    return RequestFactory()


@pytest.fixture
def now():
    """Current timezone-aware datetime"""
    return timezone.now()


@pytest.fixture
def future_datetime(now):
    """Datetime 1 hour in the future"""
    return now + timedelta(hours=1)


@pytest.fixture
def past_datetime(now):
    """Datetime 1 hour in the past"""
    return now - timedelta(hours=1)


@pytest.fixture
def far_future_datetime(now):
    """Datetime 1 day in the future"""
    return now + timedelta(days=1)


@pytest.fixture
def far_past_datetime(now):
    """Datetime 1 day in the past"""
    return now - timedelta(days=1)



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
