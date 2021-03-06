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
from foundation.models import Store, Product, Shipper, User, CropLifeCycleStage, CropCondition, CropDataSheet, CropSubstrate


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
        #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
        #                           LIFE CYCLE STAGES                          #
        #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
        CropLifeCycleStage.objects.update_or_create(id=1,  defaults={ 'type_of': CropLifeCycleStage.TYPE_OF.PLANT,     'order_number': 1,  'name': "Germinating",       'slug': 'germinating',})
        CropLifeCycleStage.objects.update_or_create(id=2,  defaults={ 'type_of': CropLifeCycleStage.TYPE_OF.PLANT,     'order_number': 2,  'name': "Growing",           'slug': 'growing',})
        CropLifeCycleStage.objects.update_or_create(id=3,  defaults={ 'type_of': CropLifeCycleStage.TYPE_OF.PLANT,     'order_number': 3,  'name': "Flowering",         'slug': 'flowering',})
        CropLifeCycleStage.objects.update_or_create(id=4,  defaults={ 'type_of': CropLifeCycleStage.TYPE_OF.PLANT,     'order_number': 4,  'name': "Fruiting",          'slug': 'fruiting',})
        CropLifeCycleStage.objects.update_or_create(id=5,  defaults={ 'type_of': CropLifeCycleStage.TYPE_OF.PLANT,     'order_number': 5,  'name': "Seeding",           'slug': 'seeding',})
        CropLifeCycleStage.objects.update_or_create(id=6,  defaults={ 'type_of': CropLifeCycleStage.TYPE_OF.PLANT,     'order_number': 6,  'name': "Dying",             'slug': 'dying',})
        CropLifeCycleStage.objects.update_or_create(id=7,  defaults={ 'type_of': CropLifeCycleStage.TYPE_OF.FISHSTOCK, 'order_number': 7,  'name': "Eggs",              'slug': 'eggs',})
        CropLifeCycleStage.objects.update_or_create(id=8,  defaults={ 'type_of': CropLifeCycleStage.TYPE_OF.FISHSTOCK, 'order_number': 8,  'name': "Embryo",            'slug': 'embryo',})
        CropLifeCycleStage.objects.update_or_create(id=9,  defaults={ 'type_of': CropLifeCycleStage.TYPE_OF.FISHSTOCK, 'order_number': 9,  'name': "Larva",             'slug': 'larva',})
        CropLifeCycleStage.objects.update_or_create(id=10, defaults={ 'type_of': CropLifeCycleStage.TYPE_OF.FISHSTOCK, 'order_number': 10, 'name': "Fry",               'slug': 'fry',})
        CropLifeCycleStage.objects.update_or_create(id=11, defaults={ 'type_of': CropLifeCycleStage.TYPE_OF.FISHSTOCK, 'order_number': 11, 'name': "Fingerling",        'slug': 'fingerling',})
        CropLifeCycleStage.objects.update_or_create(id=12, defaults={ 'type_of': CropLifeCycleStage.TYPE_OF.FISHSTOCK, 'order_number': 12, 'name': "Adult Fish",        'slug': 'adult-fish',})
        CropLifeCycleStage.objects.update_or_create(id=13, defaults={ 'type_of': CropLifeCycleStage.TYPE_OF.FISHSTOCK, 'order_number': 13, 'name': "Death",             'slug': 'death',})

        #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
        #                               SUBSTRATE                              #
        #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
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

        #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
        #                       CROP DATA SHEET & CONDITION                    #
        #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
        #-----------------------------------------------------------------------
        #                            DEFAULT OPTION
        #-----------------------------------------------------------------------
        CropDataSheet.objects.update_or_create(
           id=1,
           defaults={
               'slug': 'other',
               'order_number': 10000,
               'type_of': CropDataSheet.TYPE_OF.NONE,
               'name': "Other"
           }
        )

        ########################################################################
        #                                PLANTS                                #
        ########################################################################
        #----------------------------------------------------------------------#
        #                               CANNABIS                               #
        #----------------------------------------------------------------------#
        crop, was_created = CropDataSheet.objects.update_or_create(
           id=2,
           defaults={
               'slug': 'cannabis',
               'order_number': 1,
               'type_of': CropDataSheet.TYPE_OF.PLANT,
               'name': "Cannabis",
               'has_day_and_night_cycle': False,
           }
        )
        crop.stages.set([1,2,3,4,5,6])

        #----------------------------------------------------------------------#
        #                               TOMATO                                 #
        #----------------------------------------------------------------------#
        crop, was_created = CropDataSheet.objects.update_or_create(
           id=3,
           defaults={
               'slug': 'tomato',
               'order_number': 2,
               'type_of': CropDataSheet.TYPE_OF.PLANT,
               'name': "Tomato",
               'has_day_and_night_cycle': True,
           }
        )
        crop.stages.set([1,2,3,4,5,6])

        # HUMIDITY
        CropCondition.objects.update_or_create(id=1, defaults={'id': 1, 'data_sheet': crop, 'stage_id': 1, 'type_of': CropCondition.INSTRUMENT_TYPE.HUMIDITY, 'max_value': 100, 'min_value': 0, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=2, defaults={'id': 2, 'data_sheet': crop, 'stage_id': 2, 'type_of': CropCondition.INSTRUMENT_TYPE.HUMIDITY, 'max_value': 100, 'min_value': 0, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=3, defaults={'id': 3, 'data_sheet': crop, 'stage_id': 3, 'type_of': CropCondition.INSTRUMENT_TYPE.HUMIDITY, 'max_value': 100, 'min_value': 0, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=4, defaults={'id': 4, 'data_sheet': crop, 'stage_id': 4, 'type_of': CropCondition.INSTRUMENT_TYPE.HUMIDITY, 'max_value': 100, 'min_value': 0, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=5, defaults={'id': 5, 'data_sheet': crop, 'stage_id': 5, 'type_of': CropCondition.INSTRUMENT_TYPE.HUMIDITY, 'max_value': 100, 'min_value': 0, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=6, defaults={'id': 6, 'data_sheet': crop, 'stage_id': 6, 'type_of': CropCondition.INSTRUMENT_TYPE.HUMIDITY, 'max_value': 100, 'min_value': 0, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})

        # DAY AIR TEMPERATURE (1)
        CropCondition.objects.update_or_create(id=7, defaults={'data_sheet': crop, 'stage_id': 1, 'type_of': CropCondition.INSTRUMENT_TYPE.DAY_AIR_TEMPERATURE, 'max_value': 26, 'min_value': 22, 'operation_cycle': CropCondition.OPERATION_CYCLE.DAY_CYCLE,})
        CropCondition.objects.update_or_create(id=8, defaults={'data_sheet': crop, 'stage_id': 2, 'type_of': CropCondition.INSTRUMENT_TYPE.DAY_AIR_TEMPERATURE, 'max_value': 26, 'min_value': 22, 'operation_cycle': CropCondition.OPERATION_CYCLE.DAY_CYCLE,})
        CropCondition.objects.update_or_create(id=9, defaults={'data_sheet': crop, 'stage_id': 3, 'type_of': CropCondition.INSTRUMENT_TYPE.DAY_AIR_TEMPERATURE, 'max_value': 26, 'min_value': 22, 'operation_cycle': CropCondition.OPERATION_CYCLE.DAY_CYCLE,})
        CropCondition.objects.update_or_create(id=10, defaults={'data_sheet': crop, 'stage_id': 4, 'type_of': CropCondition.INSTRUMENT_TYPE.DAY_AIR_TEMPERATURE, 'max_value': 26, 'min_value': 22, 'operation_cycle': CropCondition.OPERATION_CYCLE.DAY_CYCLE,})
        CropCondition.objects.update_or_create(id=11, defaults={'data_sheet': crop, 'stage_id': 5, 'type_of': CropCondition.INSTRUMENT_TYPE.DAY_AIR_TEMPERATURE, 'max_value': 26, 'min_value': 22, 'operation_cycle': CropCondition.OPERATION_CYCLE.DAY_CYCLE,})
        CropCondition.objects.update_or_create(id=12, defaults={'data_sheet': crop, 'stage_id': 6, 'type_of': CropCondition.INSTRUMENT_TYPE.DAY_AIR_TEMPERATURE, 'max_value': 26, 'min_value': 22, 'operation_cycle': CropCondition.OPERATION_CYCLE.DAY_CYCLE,})

        # NIGHT AIR TEMPERATURE (1)
        CropCondition.objects.update_or_create(id=13, defaults={'data_sheet': crop, 'stage_id': 1, 'type_of': CropCondition.INSTRUMENT_TYPE.NIGHT_AIR_TEMPERATURE, 'max_value': 16, 'min_value': 12, 'operation_cycle': CropCondition.OPERATION_CYCLE.NIGHT_CYCLE,})
        CropCondition.objects.update_or_create(id=14, defaults={'data_sheet': crop, 'stage_id': 2, 'type_of': CropCondition.INSTRUMENT_TYPE.NIGHT_AIR_TEMPERATURE, 'max_value': 16, 'min_value': 12, 'operation_cycle': CropCondition.OPERATION_CYCLE.NIGHT_CYCLE,})
        CropCondition.objects.update_or_create(id=15, defaults={'data_sheet': crop, 'stage_id': 3, 'type_of': CropCondition.INSTRUMENT_TYPE.NIGHT_AIR_TEMPERATURE, 'max_value': 16, 'min_value': 12, 'operation_cycle': CropCondition.OPERATION_CYCLE.NIGHT_CYCLE,})
        CropCondition.objects.update_or_create(id=16, defaults={'data_sheet': crop, 'stage_id': 4, 'type_of': CropCondition.INSTRUMENT_TYPE.NIGHT_AIR_TEMPERATURE, 'max_value': 16, 'min_value': 12, 'operation_cycle': CropCondition.OPERATION_CYCLE.NIGHT_CYCLE,})
        CropCondition.objects.update_or_create(id=17, defaults={'data_sheet': crop, 'stage_id': 5, 'type_of': CropCondition.INSTRUMENT_TYPE.NIGHT_AIR_TEMPERATURE, 'max_value': 16, 'min_value': 12, 'operation_cycle': CropCondition.OPERATION_CYCLE.NIGHT_CYCLE,})
        CropCondition.objects.update_or_create(id=18, defaults={'data_sheet': crop, 'stage_id': 6, 'type_of': CropCondition.INSTRUMENT_TYPE.NIGHT_AIR_TEMPERATURE, 'max_value': 16, 'min_value': 12, 'operation_cycle': CropCondition.OPERATION_CYCLE.NIGHT_CYCLE,})

        # PPM (TVOC) (2)
        CropCondition.objects.update_or_create(id=19, defaults={'data_sheet': crop, 'stage_id': 1, 'type_of': CropCondition.INSTRUMENT_TYPE.TVOC, 'min_value': 1400, 'max_value': 3500, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=20, defaults={'data_sheet': crop, 'stage_id': 2, 'type_of': CropCondition.INSTRUMENT_TYPE.TVOC, 'min_value': 1400, 'max_value': 3500, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=21, defaults={'data_sheet': crop, 'stage_id': 3, 'type_of': CropCondition.INSTRUMENT_TYPE.TVOC, 'min_value': 1400, 'max_value': 3500, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=22, defaults={'data_sheet': crop, 'stage_id': 4, 'type_of': CropCondition.INSTRUMENT_TYPE.TVOC, 'min_value': 1400, 'max_value': 3500, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=23, defaults={'data_sheet': crop, 'stage_id': 5, 'type_of': CropCondition.INSTRUMENT_TYPE.TVOC, 'min_value': 1400, 'max_value': 3500, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=24, defaults={'data_sheet': crop, 'stage_id': 6, 'type_of': CropCondition.INSTRUMENT_TYPE.TVOC, 'min_value': 1400, 'max_value': 3500, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})

        # CO2 (3)
        CropCondition.objects.update_or_create(id=25, defaults={'data_sheet': crop, 'stage_id': 1, 'type_of': CropCondition.INSTRUMENT_TYPE.CO2, 'max_value': 1000, 'min_value': 600, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=26, defaults={'data_sheet': crop, 'stage_id': 2, 'type_of': CropCondition.INSTRUMENT_TYPE.CO2, 'max_value': 1000, 'min_value': 600, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=27, defaults={'data_sheet': crop, 'stage_id': 3, 'type_of': CropCondition.INSTRUMENT_TYPE.CO2, 'max_value': 1000, 'min_value': 600, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=28, defaults={'data_sheet': crop, 'stage_id': 4, 'type_of': CropCondition.INSTRUMENT_TYPE.CO2, 'max_value': 1000, 'min_value': 600, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=29, defaults={'data_sheet': crop, 'stage_id': 5, 'type_of': CropCondition.INSTRUMENT_TYPE.CO2, 'max_value': 1000, 'min_value': 600, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=30, defaults={'data_sheet': crop, 'stage_id': 6, 'type_of': CropCondition.INSTRUMENT_TYPE.CO2, 'max_value': 1000, 'min_value': 600, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})

        # WATER TEMPERATURE (4)
        CropCondition.objects.update_or_create(id=31, defaults={'data_sheet': crop, 'stage_id': 1, 'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 26, 'min_value': 18, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=32, defaults={'data_sheet': crop, 'stage_id': 2, 'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 26, 'min_value': 18, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=33, defaults={'data_sheet': crop, 'stage_id': 3, 'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 26, 'min_value': 18, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=34, defaults={'data_sheet': crop, 'stage_id': 4, 'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 26, 'min_value': 18, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=35, defaults={'data_sheet': crop, 'stage_id': 5, 'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 26, 'min_value': 18, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=36, defaults={'data_sheet': crop, 'stage_id': 6, 'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 26, 'min_value': 18, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})

        # PH (1)
        CropCondition.objects.update_or_create(id=37, defaults={'data_sheet': crop, 'stage_id': 1, 'type_of': CropCondition.INSTRUMENT_TYPE.PH, 'max_value': 6.5, 'min_value': 5.5, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=38, defaults={'data_sheet': crop, 'stage_id': 2, 'type_of': CropCondition.INSTRUMENT_TYPE.PH, 'max_value': 6.5, 'min_value': 5.5, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=39, defaults={'data_sheet': crop, 'stage_id': 3, 'type_of': CropCondition.INSTRUMENT_TYPE.PH, 'max_value': 6.5, 'min_value': 5.5, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=40, defaults={'data_sheet': crop, 'stage_id': 4, 'type_of': CropCondition.INSTRUMENT_TYPE.PH, 'max_value': 6.5, 'min_value': 5.5, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=41, defaults={'data_sheet': crop, 'stage_id': 5, 'type_of': CropCondition.INSTRUMENT_TYPE.PH, 'max_value': 6.5, 'min_value': 5.5, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=42, defaults={'data_sheet': crop, 'stage_id': 6, 'type_of': CropCondition.INSTRUMENT_TYPE.PH, 'max_value': 6.5, 'min_value': 5.5, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})

        # EC (2)
        CropCondition.objects.update_or_create(id=43, defaults={'data_sheet': crop, 'stage_id': 1, 'type_of': CropCondition.INSTRUMENT_TYPE.EC, 'max_value': 50, 'min_value': 20, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=44, defaults={'data_sheet': crop, 'stage_id': 2, 'type_of': CropCondition.INSTRUMENT_TYPE.EC, 'max_value': 50, 'min_value': 20, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=45, defaults={'data_sheet': crop, 'stage_id': 3, 'type_of': CropCondition.INSTRUMENT_TYPE.EC, 'max_value': 50, 'min_value': 20, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=46, defaults={'data_sheet': crop, 'stage_id': 4, 'type_of': CropCondition.INSTRUMENT_TYPE.EC, 'max_value': 50, 'min_value': 20, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=47, defaults={'data_sheet': crop, 'stage_id': 5, 'type_of': CropCondition.INSTRUMENT_TYPE.EC, 'max_value': 50, 'min_value': 20, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=48, defaults={'data_sheet': crop, 'stage_id': 6, 'type_of': CropCondition.INSTRUMENT_TYPE.EC, 'max_value': 50, 'min_value': 20, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})

        # ORP
        CropCondition.objects.update_or_create(id=49, defaults={'data_sheet': crop, 'stage_id': 1, 'type_of': CropCondition.INSTRUMENT_TYPE.ORP, 'max_value': 100, 'min_value': 0, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=50, defaults={'data_sheet': crop, 'stage_id': 2, 'type_of': CropCondition.INSTRUMENT_TYPE.ORP, 'max_value': 100, 'min_value': 0, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=51, defaults={'data_sheet': crop, 'stage_id': 3, 'type_of': CropCondition.INSTRUMENT_TYPE.ORP, 'max_value': -40, 'min_value': 60, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=52, defaults={'data_sheet': crop, 'stage_id': 4, 'type_of': CropCondition.INSTRUMENT_TYPE.ORP, 'max_value': -40, 'min_value': 60, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=53, defaults={'data_sheet': crop, 'stage_id': 5, 'type_of': CropCondition.INSTRUMENT_TYPE.ORP, 'max_value': -40, 'min_value': 60, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=54, defaults={'data_sheet': crop, 'stage_id': 6, 'type_of': CropCondition.INSTRUMENT_TYPE.ORP, 'max_value': -40, 'min_value': 60, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})

        ########################################################################
        #                              FISHSTOCK                               #
        ########################################################################
        #----------------------------------------------------------------------#
        #                              Goldfish                                #
        #----------------------------------------------------------------------#
        crop, was_created = CropDataSheet.objects.update_or_create(
           id=1000,
           defaults={
               'slug': 'goldfish',
               'order_number': 1000,
               'type_of': CropDataSheet.TYPE_OF.FISHSTOCK,
               'name': "Goldfish",
               'has_day_and_night_cycle': True,
           }
        )
        crop.stages.set([7,8,9,10,11,12,13])

        # WATER TEMPERATURE (1)
        CropCondition.objects.update_or_create(id=100,  defaults={'data_sheet': crop, 'stage_id': 7,  'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 32, 'min_value': 2, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=101,  defaults={'data_sheet': crop, 'stage_id': 8,  'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 32, 'min_value': 2, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=102,  defaults={'data_sheet': crop, 'stage_id': 9,  'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 32, 'min_value': 2, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=103, defaults={'data_sheet': crop, 'stage_id': 10, 'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 32, 'min_value': 2, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=104, defaults={'data_sheet': crop, 'stage_id': 11, 'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 32, 'min_value': 2, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=105, defaults={'data_sheet': crop, 'stage_id': 12, 'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 32, 'min_value': 2, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=106, defaults={'data_sheet': crop, 'stage_id': 13, 'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 32, 'min_value': 2, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})

        #----------------------------------------------------------------------#
        #                               Tilapia                                #
        #----------------------------------------------------------------------#
        crop, was_created = CropDataSheet.objects.update_or_create(
           id=1001,
           defaults={
               'slug': 'tilapia',
               'order_number': 1001,
               'type_of': CropDataSheet.TYPE_OF.FISHSTOCK,
               'name': "Tilapia",
               'has_day_and_night_cycle': True,
           }
        )
        crop.stages.set([7,8,9,10,11,12,13])

        # WATER TEMPERATURE (1)
        CropCondition.objects.update_or_create(id=201,  defaults={'data_sheet': crop, 'stage_id': 7,  'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 32, 'min_value': 15, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=202,  defaults={'data_sheet': crop, 'stage_id': 8,  'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 32, 'min_value': 15, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=203,  defaults={'data_sheet': crop, 'stage_id': 9,  'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 32, 'min_value': 15, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=204, defaults={'data_sheet': crop, 'stage_id': 10, 'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 32, 'min_value': 15, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=205, defaults={'data_sheet': crop, 'stage_id': 11, 'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 32, 'min_value': 15, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=206, defaults={'data_sheet': crop, 'stage_id': 12, 'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 32, 'min_value': 15, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})
        CropCondition.objects.update_or_create(id=207, defaults={'data_sheet': crop, 'stage_id': 13, 'type_of': CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE, 'max_value': 32, 'min_value': 15, 'operation_cycle': CropCondition.OPERATION_CYCLE.CONTINUOUS_CYCLE,})

        # DEVELOPER NOTES:
        # (1) HLA-6721-7 - Adapted from Appendix 1 of Somerville, C., and et. Al. 2014. Small-scale aquaponic food production. Integrated fish and plant farming. FAO Fisheries and Aquaculture Technical Paper No. 589. VIA http://pods.dasnr.okstate.edu/docushare/dsweb/Get/Document-10035/HLA-6721web.pdf by Aquaponics - OSU Fact Sheets - Oklahoma State University.
        # (2) https://growguru.co.za/blogs/hydroponic/ph-tds-ppm-ec-levels-for-hydroponic-vegetables
        # (3) CO2 - http://magazine.aga.com/better-greenhouses-tomatoes-with-co2/
        # (4) WATER TEMP - https://www.gardeningknowhow.com/special/containers/hydroponic-water-temperature.htm
        # (5) HOW AQUAPONICS WORKS - https://aces.nmsu.edu/pubs/_circulars/CR680/welcome.html
