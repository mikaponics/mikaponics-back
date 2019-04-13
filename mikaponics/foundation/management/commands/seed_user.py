# -*- coding: utf-8 -*-
import logging
import os
import sys
from decimal import *
from django.db.models import Sum
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from djmoney.money import Money
from oauthlib.common import generate_token

from foundation.models import Store, Product, Shipper
from foundation.models import User, Device, Instrument, TimeSeriesDatum


class Command(BaseCommand):
    help = _('Populates the user account with random test data.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py seed_user "bart@mikasoftware.com" 3 5000
        """
        parser.add_argument('email', nargs='+', type=str)
        parser.add_argument('numb_of_devices', nargs='+', type=int)
        parser.add_argument('numb_of_tsd', nargs='+', type=int)

    def handle(self, *args, **options):
        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('SEED: Starting our database seeding...'))
        )

        # Extract the input.
        email = options['email'][0]
        numb_of_devices = options['numb_of_devices'][0]
        numb_of_tsd = options['numb_of_tsd'][0]

        product = Product.objects.first()

        # STEP 1: lookup our user by email.
        try:
            user = User.objects.get(email=email)
        except Exception as e:
            raise CommandError(_('Email does not exist, please pick another email.'))

        # STEP 2: Create our devices per user.
        self.stdout.write(
            self.style.SUCCESS(_('SEED: Seeding devices...'))
        )
        devices = Device.objects.seed(user, product, numb_of_devices)

        # Step 3: Create our instruments per device.
        for device in devices:
            # NOTE: 1 & 2 are the unique `type_of` values.
            for type_of in [1,2]:
                self.stdout.write(
                    self.style.SUCCESS(_('SEED: Seeding instrument for device ID # %(id)s...')%{
                        'id': str(device.id)
                    })
                )
                instrument = Instrument.objects.create(
                    device = device,
                    type_of = type_of,
                    configuration = {"serial_number": 538319, "channel_number": 0, "hub_port_number": 0},
                )

                # Step 4: Create our time-series data per instrument.
                self.stdout.write(
                    self.style.SUCCESS(_('SEED: Seeding time-series data for instrument ID # %(iid)s in device ID # %(did)s...')%{
                        'iid': str(instrument.id),
                        'did': str(device.id),
                    })
                )
                tsd = TimeSeriesDatum.objects.seed(instrument, numb_of_tsd)

                # Step 5: Save the last recorded value.
                last_datum = tsd[0]
                instrument.last_measured_value = last_datum.value
                instrument.last_measured_timestamp = last_datum.timestamp
                instrument.save()
                device.last_measured_value = last_datum.value
                device.last_measured_at = last_datum.timestamp
                device.last_measured_unit_of_measure = last_datum.get_unit_of_measure()
                device.save()

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('SEED: Finished our database seeding.'))
        )
