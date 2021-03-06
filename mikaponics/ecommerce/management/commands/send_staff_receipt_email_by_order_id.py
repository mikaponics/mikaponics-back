# -*- coding: utf-8 -*-
import django_rq
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMultiAlternatives    # EMAILER
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string    # HTML to TXT

from foundation.models import Invoice
from foundation import constants
from foundation.utils import reverse_with_full_domain
from foundation.model_resources import get_staff_email_addresses


class Command(BaseCommand):
    """
    Example:
    python manage.py send_staff_receipt_email_by_order_id 1
    """
    help = _('Command will send an receipt email to all the staff based on the invoice ID.')

    def add_arguments(self, parser):
        parser.add_argument('invoice_id' , nargs='+', type=int)

    def handle(self, *args, **options):
        try:
            for invoice_id in options['invoice_id']:
                invoice = Invoice.objects.get(id=invoice_id)
                self.begin_processing(invoice)
        except Invoice.DoesNotExist:
            raise CommandError(_('Invoice ID does not exist for value: %s') % str(invoice_id))

        # Return success message.
        self.stdout.write(
            self.style.SUCCESS(_('MIKAPONICS: Send receipt email to staff was sent successfully.'))
        )

    def begin_processing(self, invoice):
        # Generate the data.
        url = settings.MIKAPONICS_BACKEND_HTTP_PROTOCOL+settings.MIKAPONICS_BACKEND_HTTP_DOMAIN+"/en/admin/foundation/user/"+str(invoice.user.id)+"/change/"
        web_view_url = reverse_with_full_domain(
            reverse_url_id='mikaponics_invoice_receipt_email',
            resolve_url_args=[invoice.id]
        )

        # Get the parameter.
        subject = "Mikaponics: Customer made purchase"
        param = {
            'constants': constants,
            'url': url,
            'web_view_url': web_view_url,
            'me': invoice.user,
            'invoice': invoice,
        }

        # Plug-in the data into our templates and render the data.
        text_content = render_to_string('store/emails/receipt_email_view.txt', param)
        html_content = render_to_string('store/emails/receipt_email_view.html', param)

        # Generate our address.
        from_email = settings.DEFAULT_FROM_EMAIL
        to = get_staff_email_addresses()

        # Send the email.
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
