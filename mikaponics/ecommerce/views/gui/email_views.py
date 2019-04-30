# -*- coding: utf-8 -*-
import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import condition

from foundation import constants
from foundation.models import User
from foundation.utils import reverse_with_full_domain


logger = logging.getLogger(__name__)


def receipt_email_page(request, pk=None):
    invoice = Invoice.objects.filter(pk=pk).first()
    if invoice is None:
        raise PermissionDenied(_('Does not exist.'))

    # Generate the data.
    url = settings.MIKAPONICS_FRONTEND_HTTP_PROTOCOL+settings.MIKAPONICS_FRONTEND_HTTP_DOMAIN+"/invoice/"+invoice.slug;
    web_view_url = reverse_with_full_domain(
        reverse_url_id='mikaponics_invoice_receipt_email',
        resolve_url_args=[invoice.id]
    )

    # Get the parameter.
    param = {
        'constants': constants,
        'url': url,
        'web_view_url': web_view_url,
        'me': request.user,
        'invoice': invoice,
    }
    # # DEVELOPERS NOTE:
    # # - When copying the "Sunday" open source email theme into our code, we will
    # #   need to use a formatter to inline the CSS.
    # # - https://templates.mailchimp.com/resources/inline-css/

    return render(request, 'store/emails/receipt_email_view.html', param)


def onboarded_email_page(request, pk=None):
    user = User.objects.filter(pk=pk).first()
    if user is None:
        raise PermissionDenied(_('Does not exist.'))

    # Generate the data.
    url = settings.MIKAPONICS_BACKEND_HTTP_PROTOCOL+settings.MIKAPONICS_BACKEND_HTTP_DOMAIN+"/en/admin/foundation/user/"+str(user.id)+"/change/"
    web_view_url = reverse_with_full_domain(
        reverse_url_id='mikaponics_onboarded_email',
        resolve_url_args=[user.id]
    )

    # Get the parameter.
    param = {
        'constants': constants,
        'url': url,
        'web_view_url': web_view_url,
        'user': user,
    }
    # # DEVELOPERS NOTE:
    # # - When copying the "Sunday" open source email theme into our code, we will
    # #   need to use a formatter to inline the CSS.
    # # - https://templates.mailchimp.com/resources/inline-css/

    return render(request, 'store/emails/onboarded_email_view.html', param)
