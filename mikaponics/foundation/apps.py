from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FoundationConfig(AppConfig):
    name = 'foundation'
    verbose_name = _('Foundation')

    def ready(self):
        import foundation.signals
