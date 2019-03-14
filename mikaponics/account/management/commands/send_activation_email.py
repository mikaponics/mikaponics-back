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

from foundation import constants
from foundation.models import User
from foundation.utils import reverse_with_full_domain


class Command(BaseCommand):
    """
    Example:
    python manage.py send_activation_email bart@mikasoftware.com
    """
    help = _('Command will send an activation email to the user based on the email.')

    def add_arguments(self, parser):
        # User Account.
        parser.add_argument('email' , nargs='+', type=str)

    def handle(self, *args, **options):
        email = options['email'][0]

        try:
            for email in options['email']:
                me = User.objects.get(email__iexact=email)
                self.begin_processing(me)
        except User.DoesNotExist:
            raise CommandError(_('Account does not exist with the email or username: %s') % str(email))

        # Return success message.
        self.stdout.write(
            self.style.SUCCESS(_('MIKAPONICS: Activation email was sent successfully.'))
        )

    def begin_processing(self, me):
        pr_access_code = me.generate_pr_code()

        # Generate the data.
        url = reverse_with_full_domain(
            reverse_url_id='mikaponics_user_activation_detail',
            resolve_url_args=[pr_access_code]
        )
        web_view_url = reverse_with_full_domain(
            reverse_url_id='mikaponics_activate_email',
            resolve_url_args=[pr_access_code]
        )
        subject = "Welcome to Mikaponics!"
        param = {
            'me': me,
            'url': url,
            'web_view_url': web_view_url,
            'constants': constants
        }

        # Plug-in the data into our templates and render the data.
        text_content = render_to_string('account/email/user_activation_email_view.txt', param)
        html_content = render_to_string('account/email/user_activation_email_view.html', param)

        # Generate our address.
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [me.email]

        # Send the email.
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
