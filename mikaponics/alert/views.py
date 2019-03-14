# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin

from foundation.mixins import MikaponicsListView, MikaponicsDetailView
from foundation.models import Device, Instrument, InstrumentAlert
from foundation.utils import reverse_with_full_domain


class AlertEmailWebBrowserView(LoginRequiredMixin, MikaponicsDetailView):
    context_object_name = 'alert'
    template_name = 'alert/email/instrument_alert_view.html'
    menu_id = "alert"
    model = InstrumentAlert

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        context = super().get_context_data(**kwargs)

        alert = context['alert']

        # Update our context.
        context['me'] = self.request.user
        context['ALERT_STATE'] = InstrumentAlert.INSTRUMENT_ALERT_STATE
        context['url'] = reverse_with_full_domain(
            reverse_url_id='mikaponics_instrument_detail',
            resolve_url_args=[alert.id]
        )
        context['web_view_url'] = reverse_with_full_domain(
            reverse_url_id='mikaponics_instrument_alerts_email',
            resolve_url_args=[alert.id]
        )

        # Return our modified context.
        return context
