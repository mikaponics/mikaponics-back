# -*- coding: utf-8 -*-
import logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import condition

from foundation import constants
from foundation.models import Order
from foundation.utils import reverse_with_full_domain


logger = logging.getLogger(__name__)


def receipt_email_page(request, pk=None):
    order = Order.objects.filter(pk=pk).first()
    if order is None:
        raise PermissionDenied(_('Does not exist.'))

    # Generate the data.
    url = reverse_with_full_domain(
        reverse_url_id='mikaponics_order_detail',
        resolve_url_args=[order.id]
    )
    web_view_url = reverse_with_full_domain(
        reverse_url_id='mikaponics_order_receipt_email',
        resolve_url_args=[order.id]
    )

    # Get the parameter.
    param = {
        'constants': constants,
        'url': url,
        'web_view_url': web_view_url,
        'me': request.user,
        'order': order,
    }
    # # DEVELOPERS NOTE:
    # # - When copying the "Sunday" open source email theme into our code, we will
    # #   need to use a formatter to inline the CSS.
    # # - https://templates.mailchimp.com/resources/inline-css/

    return render(request, 'store/emails/receipt_email_view.html', param)
