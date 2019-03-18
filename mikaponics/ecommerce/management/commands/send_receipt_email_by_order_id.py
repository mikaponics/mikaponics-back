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

from foundation.models import Order
from foundation import constants
from foundation.utils import reverse_with_full_domain


class Command(BaseCommand):
    """
    Example:
    python manage.py send_receipt_email_by_order_id 1
    """
    help = _('Command will send an receipt email to the user based on the order ID.')

    def add_arguments(self, parser):
        parser.add_argument('order_id' , nargs='+', type=int)

    def handle(self, *args, **options):
        try:
            for order_id in options['order_id']:
                order = Order.objects.get(id=order_id)
                self.begin_processing(order)
        except Order.DoesNotExist:
            raise CommandError(_('Order ID does not exist.'))

        # Return success message.
        self.stdout.write(
            self.style.SUCCESS(_('MIKAPONICS: Activation email was sent successfully.'))
        )

    def begin_processing(self, order):
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
        subject = "Mikaponics: Your Receipt is Ready"
        param = {
            'constants': constants,
            'url': url,
            'web_view_url': web_view_url,
            'me': order.user,
            'order': order,
        }

        # Plug-in the data into our templates and render the data.
        text_content = render_to_string('store/emails/receipt_email_view.txt', param)
        html_content = render_to_string('store/emails/receipt_email_view.html', param)

        # Generate our address.
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [order.user.email]

        # Send the email.
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
