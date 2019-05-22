# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMultiAlternatives    # EMAILER
from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models import Q
from django.template.loader import render_to_string    # HTML to TXT
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from foundation.constants import *
from foundation.models import AlertItem
from foundation.utils import reverse_with_full_domain


class Command(BaseCommand):
    help = _('Command will send alert email to user about their production.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py send_production_alert_email 1
        """
        parser.add_argument('id', nargs='+', type=int)

    def handle(self, *args, **options):
        """
        Either check the device for the inputted `id` value or check all devices.
        """
        utc_today = timezone.now()

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | SPAE | Started running.') % {
                'dt': str(timezone.now())
            })
        )

        try:
            for id in options['id']:
                alert = AlertItem.objects.get(id=id)
                self.begin_processing(alert)

        except AlertItem.DoesNotExist:
            # For debugging purposes only.
            raise CommandError(_('%(dt)s | SPAE | Alert does not exist with the id.') % {
                'dt': str(timezone.now())
            })

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | SPAE | Finished running.') % {
                'dt': str(timezone.now())
            })
        )

    def begin_processing(self, alert):
        me = alert.production.user
        production = alert.production

        # Generate the links.
        url = settings.MIKAPONICS_FRONTEND_HTTP_PROTOCOL+settings.MIKAPONICS_FRONTEND_HTTP_DOMAIN+alert.production.get_absolute_url()
        web_view_url = reverse_with_full_domain(
            reverse_url_id='mikaponics_alert_items_email',
            resolve_url_args=[alert.id]
        )
        subject = "Mikaponics: Alert Notification"
        param = {
            'alert': alert,
            'url': url,
            'web_view_url': web_view_url,
            'me': me
        }

        # For debugging purposes only.
        print("---------------------------------------------------------------")
        print("URL", url)
        print("WEB URL", web_view_url)
        print("---------------------------------------------------------------")

        # DEVELOPERS NOTE:
        # https://templates.mailchimp.com/resources/inline-css/

        # Plug-in the data into our templates and render the data.
        text_content = render_to_string('alert/email/production_alert_email_view.txt', param)
        html_content = render_to_string('alert/email/production_alert_email_view.html', param)

        # Generate our address.
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [me.email]

        # Send the email.
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | SPAE | Sent alert email to %(email)s.') % {
                'dt': str(timezone.now()),
                'email': me.email
            })
        )
