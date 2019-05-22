# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from foundation import constants
from foundation.models import Production, TimeSeriesDatum
from foundation.model_resources import create_production_alert_item_in_system_if_possible


class Command(BaseCommand):
    help = _('Command will look at productions and will either generate alert or do nothing.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py production_alert_monitor 1
        """
        parser.add_argument('id', nargs='+', type=int)

    @transaction.atomic
    def handle(self, *args, **options):
        """
        Either check the device for the inputted `id` value or check all devices.
        """
        utc_today = timezone.now()
        utc_today_minus_some_minutes = utc_today - timedelta(minutes=5)

        # Get user input.
        id = options['id'][0]

        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | PAM | Started running for production # %(id)s.') % {
                'dt': str(timezone.now()),
                'id': str(id),
            })
        )

        # Lookup the device or error.
        try:
            production = Production.objects.select_for_update().get(id=id)
        except Production.DoesNotExist:
            raise CommandError(_('Production was not found.'))

        # Run our processing.
        self.begin_processing(production, utc_today, utc_today_minus_some_minutes)

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | PAM | Finished running for production # %(id)s.') % {
                'dt': str(timezone.now()),
                'id': str(id),
            })
        )

    def begin_processing(self, production, utc_today, utc_today_minus_some_minutes):
        alert_item = create_production_alert_item_in_system_if_possible(production)
        if alert_item:
            self.stdout.write(
                self.style.SUCCESS(_('%(dt)s | PAM | Created alert #%(aid)s for production #%(pid)s.') % {
                    'dt': str(timezone.now()),
                    'aid': str(alert_item.id),
                    'pid': str(production.id),
                })
            )
            call_command('send_production_alert_email', alert_item.id, verbosity=0)
