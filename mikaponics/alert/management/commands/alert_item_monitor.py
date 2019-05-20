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
from foundation.models import Instrument
from foundation.model_resources import (
    instrument_find_alarming_datum_in_system,
    create_instrument_alert_in_system_if_possible
)


class Command(BaseCommand):
    help = _('Command will look at instrument and either generate alert or do nothing.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py alert_item_monitor 1
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
            self.style.SUCCESS(_('%(dt)s | IAM | Started running for instrument # %(id)s.') % {
                'dt': str(timezone.now()),
                'id': str(id),
            })
        )

        # Lookup the device or error.
        try:
            instrument = Instrument.objects.select_for_update().get(id=id)
        except Instrument.DoesNotExist:
            raise CommandError(_('Instrument was not found.'))

        # Run our processing.
        self.process_instrument(instrument, utc_today, utc_today_minus_some_minutes)

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | IAM | Finished running for instrument # %(id)s.') % {
                'dt': str(timezone.now()),
                'id': str(id),
            })
        )

    def process_instrument(self, instrument, utc_today, utc_today_minus_some_minutes):
        datum, alert_state = instrument_find_alarming_datum_in_system(instrument, utc_today_minus_some_minutes, utc_today)
        if datum:
            create_instrument_alert_in_system_if_possible(instrument, datum)
