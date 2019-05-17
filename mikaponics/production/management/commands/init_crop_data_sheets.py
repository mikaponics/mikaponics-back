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
from foundation.models import Store, Product, Shipper, User, CropDataSheet, CropSubstrate


class Command(BaseCommand):
    """
    EXAMPLE:
    python manage.py init_crop_data_sheets
    """

    help = _('Sets up the crop data sheet objects in our system.')

    def handle(self, *args, **options):
        '''
        Create our data for crops.
        '''
        # SUBSTRATE
        #-----------------------------------------------------------------------
        CropSubstrate.objects.update_or_create(id=1, defaults={ 'type_of': 1, 'order_number': 10000, 'name': "Other (Please specify)",       'slug': 'other',})
        CropSubstrate.objects.update_or_create(id=2, defaults={ 'type_of': 1, 'order_number': 1,     'name': "Clay Pebbles",                 'slug': 'clay-pebbles',})
        CropSubstrate.objects.update_or_create(id=3, defaults={ 'type_of': 1, 'order_number': 2,     'name': "River Rock",                   'slug': 'river-rock',})
        CropSubstrate.objects.update_or_create(id=4, defaults={ 'type_of': 1, 'order_number': 3,     'name': "Perlite",                      'slug': 'perlite',})
        CropSubstrate.objects.update_or_create(id=5, defaults={ 'type_of': 1, 'order_number': 4,     'name': "Rockwool",                     'slug': 'rockwool',})
        CropSubstrate.objects.update_or_create(id=6, defaults={ 'type_of': 1, 'order_number': 5,     'name': "Coco coir",                    'slug': 'coco-coir',})
        CropSubstrate.objects.update_or_create(id=7, defaults={ 'type_of': 1, 'order_number': 6,     'name': "Vermiculite",                  'slug': 'vermiculite',})
        CropSubstrate.objects.update_or_create(id=8, defaults={ 'type_of': 1, 'order_number': 7,     'name': "Oasis Cubes",                  'slug': 'oasis-cubes',})
        CropSubstrate.objects.update_or_create(id=9, defaults={ 'type_of': 1, 'order_number': 8,     'name': "Floral Foam",                  'slug': 'floral-foam',})
        CropSubstrate.objects.update_or_create(id=10, defaults={'type_of': 1, 'order_number': 9,    'name': "Pine Shaving",                 'slug': 'pine-shaving',})
        CropSubstrate.objects.update_or_create(id=11, defaults={'type_of': 1, 'order_number': 10,   'name': "Sand",                         'slug': 'sand',})
        CropSubstrate.objects.update_or_create(id=12, defaults={'type_of': 1, 'order_number': 11,   'name': "Rice Hulls",                   'slug': 'rice-hulls',})
        CropSubstrate.objects.update_or_create(id=13, defaults={'type_of': 1, 'order_number': 12,   'name': "Peat Moss",                    'slug': 'peat-moss',})
        CropSubstrate.objects.update_or_create(id=14, defaults={'type_of': 1, 'order_number': 13,   'name': "Gravel",                       'slug': 'gravel',})
        CropSubstrate.objects.update_or_create(id=15, defaults={'type_of': 1, 'order_number': 14,   'name': "Diatomite",                    'slug': 'diatomite',})
        CropSubstrate.objects.update_or_create(id=16, defaults={'type_of': 1, 'order_number': 15,   'name': "Glass",                        'slug': 'glass',})
        CropSubstrate.objects.update_or_create(id=17, defaults={'type_of': 1, 'order_number': 16,   'name': "Composted and aged Pine bark", 'slug': 'composted-and-aged-pine-bark',})
        CropSubstrate.objects.update_or_create(id=18, defaults={'type_of': 1, 'order_number': 17,   'name': "Polyurethane foam insulation", 'slug': 'polyurethane-foam-insulation',})
        CropSubstrate.objects.update_or_create(id=19, defaults={'type_of': 1, 'order_number': 18,   'name': "Water absorbing crystals",     'slug': 'water-absorbing-crystals',})
        CropSubstrate.objects.update_or_create(id=20, defaults={'type_of': 2, 'order_number': 1,    'name': "Fresh Water",                  'slug': 'fresh-water',})
        CropSubstrate.objects.update_or_create(id=21, defaults={'type_of': 2, 'order_number': 2,    'name': "Salt Water",                   'slug': 'salt-water',})

        # DEFAULT OPTION
        #-----------------------------------------------------------------------
        CropDataSheet.objects.update_or_create(
           id=1,
           defaults={
               'slug': 'other',
               'order_number': 10000,
               'type_of': CropDataSheet.TYPE_OF.NONE,
               'name': "Other",
               'stages_dict': [],
               'life_dict': {}
           }
        )

        # PLANTS
        #-----------------------------------------------------------------------
        CropDataSheet.objects.update_or_create(
           id=2,
           defaults={
               'slug': 'cannabis',
               'order_number': 1,
               'type_of': CropDataSheet.TYPE_OF.PLANT,
               'name': "Cannabis",
               'stages_dict': [
                   {'id': 1, 'value': 'Germinating'},
                   {'id': 2, 'value': 'Growing'},
                   {'id': 3, 'value': 'Flowering'},
                   {'id': 4, 'value': 'Fruiting'},
                   {'id': 5, 'value': 'Seeding'},
                   {'id': 6, 'value': 'Dying'},
               ],
               'life_dict': {}
           }
        )
        CropDataSheet.objects.update_or_create(
           id=3,
           defaults={
               'slug': 'tomato',
               'order_number': 2,
               'type_of': CropDataSheet.TYPE_OF.PLANT,
               'name': "Tomato",
               'stages_dict': [
                   {'id': 1, 'value': 'Germinating'},
                   {'id': 2, 'value': 'Growing'},
                   {'id': 3, 'value': 'Flowering'},
                   {'id': 4, 'value': 'Fruiting'},
                   {'id': 5, 'value': 'Seeding'},
                   {'id': 6, 'value': 'Dying'},
               ],
               'life_dict': {}
           }
        )
        CropDataSheet.objects.update_or_create(
           id=4,
           defaults={
               'slug': 'tomato-kumato',
               'order_number': 3,
               'type_of': CropDataSheet.TYPE_OF.PLANT,
               'name': "Tomato (Kumato)",
               'stages_dict': [
                   {'id': 1, 'value': 'Germinating'},
                   {'id': 2, 'value': 'Growing'},
                   {'id': 3, 'value': 'Flowering'},
                   {'id': 4, 'value': 'Fruiting'},
                   {'id': 5, 'value': 'Seeding'},
                   {'id': 6, 'value': 'Dying'},
               ],
               'life_dict': {}
           }
        )

        # FISHSTOCK
        #-----------------------------------------------------------------------
        CropDataSheet.objects.update_or_create(
           id=1000,
           defaults={
               'slug': 'goldfish',
               'order_number': 1000,
               'type_of': CropDataSheet.TYPE_OF.FISHSTOCK,
               'name': "Goldfish",
               'stages_dict': [
                   {'id': 1, 'value': 'Eggs'},
                   {'id': 2, 'value': 'Embryo'},
                   {'id': 3, 'value': 'Larva'},
                   {'id': 4, 'value': 'Fry'},
                   {'id': 5, 'value': 'Fingerling'},
                   {'id': 6, 'value': 'Adult Fish'},
               ],
               'life_dict': {}
           }
        )
        CropDataSheet.objects.update_or_create(
           id=1001,
           defaults={
               'slug': 'tilapia',
               'order_number': 1001,
               'type_of': CropDataSheet.TYPE_OF.FISHSTOCK,
               'name': "Tilapia",
               'stages_dict': [
                   {'id': 1, 'value': 'Eggs'},
                   {'id': 2, 'value': 'Embryo'},
                   {'id': 3, 'value': 'Larva'},
                   {'id': 4, 'value': 'Fry'},
                   {'id': 5, 'value': 'Fingerling'},
                   {'id': 6, 'value': 'Adult Fish'},
               ],
               'life_dict': {}
           }
        )