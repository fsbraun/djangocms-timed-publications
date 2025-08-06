# Changelog

## [0.2.0] - 2025-08-06

- Configuration option `DJANGOCMS_TIMED_PUBLISHING_BUTTON` to always show time selection modal or use menu-based approach

## [0.1.0] - 2025-08-01

- Initial release of djangocms-timed-publishing
- Core functionality for time-limited content publication
- `TimedPublishingInterval` model for managing visibility periods
- `TimedPublishingForm` for setting publication start/end times
- Integration with djangocms-versioning to extend version management
- Admin interface with custom publish view supporting time restrictions
- Toolbar integration showing visibility status information
- Support for publishing content with optional start and end dates
- Visibility state indicators (Pending, Expired) in admin interface
- Content filtering based on time restrictions in public views
- Multi-language support (English and German translations)
- Comprehensive test coverage with pytest
- Support for Django 4.2, 5.0, 5.1, 5.2
- Support for django CMS 4.1, 5.0
- Support for Python 3.9, 3.10, 3.11, 3.12, 3.13
