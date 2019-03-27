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
from foundation.models import InstrumentAlert, Device, TimeSeriesDatum


class Command(BaseCommand):
    help = _('Command will look at device or devices and determine their state.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py check_devices 1
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
            self.style.SUCCESS(_('%(dt)s | CD | Started running for device # %(id)s.') % {
                'dt': str(timezone.now()),
                'id': str(id),
            })
        )

        # Lookup the device or error.
        try:
            device = Device.objects.select_for_update().get(id=id)
        except Device.DoesNotExist:
            raise CommandError(_('Device was not found.'))

        # Run our processing.
        self.process_device(device, utc_today_minus_some_minutes)

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | CD | Finished running for device # %(id)s.') % {
                'dt': str(timezone.now()),
                'id': str(id),
            })
        )

    def process_device(self, device, utc_today_minus_some_minutes):
        self.process_offline_status(device, utc_today_minus_some_minutes)

    def process_offline_status(self, device, utc_today_minus_some_minutes):
        """
        If the device last updated time was less then the specified amount
        then we need to set the status of the device to be offline.
        """
        last_measured_utc_timestamp = device.last_measured_at

        '''
        Process online devices.
        '''
        if device.state == Device.DEVICE_STATE.ONLINE:
            if last_measured_utc_timestamp < utc_today_minus_some_minutes:
                device.state = Device.DEVICE_STATE.OFFLINE
                device.save()
                self.stdout.write(
                    self.style.WARNING(_('%(dt)s | CD | Device # %(id)s has become offline.') % {
                        'id': str(device.id),
                        'dt': str(timezone.now())
                    })
                )
