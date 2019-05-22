# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

from foundation.mixins import MikaponicsListView, MikaponicsDetailView
from foundation.models import Device, Instrument, AlertItem
from foundation.utils import reverse_with_full_domain


class InstrumentAlertEmailWebBrowserView(LoginRequiredMixin, MikaponicsDetailView):
    context_object_name = 'alert'
    template_name = 'alert/email/instrument_alert_view.html'
    menu_id = "alert"
    model = AlertItem

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        context = super().get_context_data(**kwargs)

        alert = context['alert']

        # Update our context.
        context['me'] = self.request.user
        context['alert'] = alert
        context['url'] = settings.MIKAPONICS_FRONTEND_HTTP_PROTOCOL+settings.MIKAPONICS_FRONTEND_HTTP_DOMAIN+alert.instrument.get_absolute_url()
        context['web_view_url'] = reverse_with_full_domain(
            reverse_url_id='mikaponics_instrument_alert_items_email',
            resolve_url_args=[alert.id]
        )

        # Return our modified context.
        return context
