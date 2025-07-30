[![PyPI version](https://badge.fury.io/py/djangocms-timed-publishing.svg)](http://badge.fury.io/py/djangocms-timed-publishing)
[![Coverage Status](https://codecov.io/gh/fsbraun/djangocms-timed-publishing/branch/master/graph/badge.svg)](https://codecov.io/gh/django-cms/djangocms-timed-publishing)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/djangocms-timed-publishing)](https://pypi.org/project/djangocms-timed-publishing/)
[![PyPI - Django Versions](https://img.shields.io/pypi/frameworkversions/django/djangocms-timed-publishing)](https://www.djangoproject.com/)
[![PyPI - django CMS Versions](https://img.shields.io/pypi/frameworkversions/django-cms/djangocms-timed-publishing)](https://www.django-cms.org/)


# djangocms-timed-publishing
django CMS Timed Publishing extends django CMS Versioning to allow for planned or limited publication of content:

![Timed Publishing](timed-publishing.jpg)

## Installation

1. Install the package using pip:

    ```bash
    pip install djangocms-timed-publishing
    ```

2. Add `'djangocms_timed_publishing'` to your `INSTALLED_APPS` in `settings.py`:

    ```python
    INSTALLED_APPS = [
         # ...
         'djangocms_timed_publishing',
         # ...
    ]
    ```

3. Run migrations:

    ```bash
    python manage.py migrate
    ```
