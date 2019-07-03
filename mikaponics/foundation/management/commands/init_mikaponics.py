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

from foundation.constants import *
from foundation.models import Store, Product, Shipper, User


class Command(BaseCommand):
    """
    EXAMPLE:
    python manage.py init_mikaponics
    """

    help = _('Sets up the web-application for the first time.')

    def handle(self, *args, **options):
        '''
        Create the default store of our application.
        '''
        store, was_created = Store.objects.update_or_create(
            id=1,
            defaults={
                'id': 1,
                'name': 'Mikaponics',
                'currency': 'CAD',
                'timezone_name': "America/Toronto",
                'tax_rates': { # http://www.calculconversion.com/sales-tax-calculator-hst-gst.html
                    'CA': {
                        'NL': 15,      # Newfoundland and Labrador
                        'PE': 15,      # Prince Edward Island
                        'NS': 15,      # Nova Scotia
                        'NB': 15,      # New Brunswick
                        'QC': 14.975,  # Quebec
                        'ON': 13,      # Ontario
                        'MB': 13,      # Manitoba
                        'SK': 11,      # Saskatchewan
                        'AB': 5,       # Alberta
                        'BC': 12,      # British Columbia
                        'YT': 5,       # Yukon
                        'NT': 5,       # Northwest Territories
                        'NU': 5,       # Nunavut
                    },
                    'international': 13,
                },
                'referrer_credit':  Money(10, 'CAD'),
                'referee_credit': Money(5, 'CAD'),
            }
        )

        '''
        Create the product which integrates with our MIKAPOD project. See via
        link: https://github.com/mikaponics/mikapod-py. This is our default
        product to offer in the onboarding code.
        '''
        Product.objects.update_or_create(
            id=MIKAPONICS_SOIL_PRODUCT_ID,
            store=store,
            defaults={
                'id': MIKAPONICS_SOIL_PRODUCT_ID,
                'store': store,
                'slug': 'soil',
                'sort_number': 1,
                'icon': 'seedling',
                'name': "Mikapod - Soil",
                "short_description": "Device used for monitoring soil based planting solution.",
                'description': 'Mikapod soil telemetry device',
                'price': Money(249.99, 'CAD'),
                'state': Product.STATE.PUBLISHED
            }
        )
        Product.objects.update_or_create(
            id=MIKAPONICS_HYDROPONICS_PRODUCT_ID,
            store=store,
            defaults={
                'id': MIKAPONICS_HYDROPONICS_PRODUCT_ID,
                'store': store,
                'slug': 'hydroponic',
                'sort_number': 2,
                'icon': 'water',
                'name': "Mikapod - Hydroponics",
                "short_description": "Device used for monitoring pure water based planting solution.",
                'description': 'Mikapod hydroponics telemetry device',
                "price": Money(249.99, 'CAD'),
                'state': Product.STATE.COMING_SOON
            }
        )
        Product.objects.update_or_create(
            id=MIKAPONICS_AQUAPONICS_PRODUCT_ID,
            store=store,
            defaults={
                'id': MIKAPONICS_AQUAPONICS_PRODUCT_ID,
                'store': store,
                'slug': 'aquaponic',
                'sort_number': 3,
                'icon': 'fish',
                'name': "Mikapod - Aquaponics",
                "short_description": "Device used for monitoring a water and aquaculture mixed planting solution.",
                'description': 'Mikapod aquaponics telemetry device',
                "price": Money(249.99, 'CAD'),
                'state': Product.STATE.COMING_SOON
            }
        )
        Product.objects.update_or_create(
            id=MIKAPONICS_ALGAE_PRODUCT_ID,
            store=store,
            defaults={
                'id': MIKAPONICS_ALGAE_PRODUCT_ID,
                'store': store,
                'slug': 'algae',
                'sort_number': 4,
                'icon': 'vial',
                'name': "Mikapod - Algae",
                "short_description": "Device used for monitoring algae (ex. Sparilina) based planting solution.",
                'description': 'Mikapod algae telemetry device',
                "price": Money(249.99, 'CAD'),
                'state': Product.STATE.COMING_SOON
            }
        )

        '''
        Create the default shipper for our store.
        '''
        Shipper.objects.update_or_create(
            id=MIKAPONICS_DEFAULT_SHIPPER_ID,
            store=store,
            name='Generic shipper',
            shipping_price=Money(amount=10,currency='CAD')
        )
