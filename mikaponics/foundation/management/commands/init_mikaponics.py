# -*- coding: utf-8 -*-
"""
Example:
python manage.py setup_resource_server_authorization "bart@mikasoftware.com"
"""
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
from foundation.models import User


class Command(BaseCommand):
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
                    'international': 13
                }
            }
        )

        '''
        Create the product which integrates with our MIKAPOD project. See via
        link: https://github.com/mikaponics/mikapod-py
        '''
        Product.objects.update_or_create(
            id=1,
            store=store,
            defaults={
                'id': 1,
                'store': store,
                'name': "Mikapod",
                "price": Money(10, 'CAD')
            }
        )

        '''
        Add support for public data feed.
        '''
        Product.objects.update_or_create(
            id=2,
            store=store,
            defaults={
                'id': 2,
                'store': store,
                'name': "Data Feed",
                "price": Money(0, 'CAD')
            }
        )

        '''
        Create the default shipper for our store.
        '''
        Shipper.objects.update_or_create(
            id=1,
            store=store,
            name='Generic shipper',
            shipping_price=Money(amount=10,currency='CAD')
        )
