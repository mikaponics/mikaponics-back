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

from ecommerce.models import Store, Product, Shipper
from foundation.models import User, Device, Instrument, TimeSeriesDatum


class Command(BaseCommand):
    help = _('Populates the database with test data.')

    def add_arguments(self, parser):
        """
        Run manually in console:
        python manage.py seed_database 1 1 10
        """
        parser.add_argument('users_count', nargs='+', type=int)
        parser.add_argument('devices_per_user_count', nargs='+', type=int)
        parser.add_argument('tsd_per_device_count', nargs='+', type=int)

    def handle(self, *args, **options):
        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('SEED: Starting our database seeding...'))
        )

        # Extract the users count.
        numb_of_users = options['users_count'][0]
        numb_of_devices = options['devices_per_user_count'][0]
        numb_of_tsd = options['tsd_per_device_count'][0]

        product = Product.objects.first()

        # STEP 1: Create our users.
        self.stdout.write(
            self.style.SUCCESS(_('SEED: Seeding users...'))
        )
        users = User.objects.seed(numb_of_users)

        # STEP 2: Create our devices per user.
        for user in users:
            self.stdout.write(
                self.style.SUCCESS(_('SEED: Seeding device...'))
            )
            devices = Device.objects.seed(user, product, numb_of_devices)

            # Step 3: Create our instruments per device.
            for device in devices:
                # NOTE: 1 & 2 are the unique `type_of` values.
                for type_of in [1,2]:
                    self.stdout.write(
                        self.style.SUCCESS(_('SEED: Seeding instrument...'))
                    )
                    instrument = Instrument.objects.create(
                        device = device,
                        type_of = type_of,
                        configuration = {},
                    )

                    # Step 4: Create our time-series data per instrument.
                    self.stdout.write(
                        self.style.SUCCESS(_('SEED: Seeding time-series data...'))
                    )
                    tsd = TimeSeriesDatum.objects.seed(instrument, numb_of_tsd)

        # For debugging purposes.
        self.stdout.write(
            self.style.SUCCESS(_('SEED: Finished our database seeding.'))
        )
