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
from foundation.models import ProblemDataSheet


class Command(BaseCommand):
    """
    EXAMPLE:
    python manage.py init_problem_data_sheets
    """

    help = _('Sets up the problem data sheet objects in our system.')

    def handle(self, *args, **options):
        '''
        Create our data sheets for indoor gardening problems.

        Special thanks:
        (1) "Preventing, Diagnosing, and Correcting Common Houseplant Problems" via link:
            https://extension.psu.edu/preventing-diagnosing-and-correcting-common-houseplant-problems
        (2) "10 Common Garden Pests—and Natural Pesticides to Keep Them Away" via link:
            https://ecowarriorprincess.net/2018/01/10-common-garden-pests-and-natural-pesticides-to-keep-them-away/
        (3) "Garden Pests" via link:
            https://www.planetnatural.com/pest-problem-solver/garden-pests/
        '''
        #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
        #                             PEST PROBLEMS                            #
        #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
        ProblemDataSheet.objects.update_or_create(id=1,    defaults={ 'id': 1,    'type_of': ProblemDataSheet.TYPE_OF.PEST, 'text': 'Ants', 'slug': 'ants'})
        ProblemDataSheet.objects.update_or_create(id=2,    defaults={ 'id': 2,    'type_of': ProblemDataSheet.TYPE_OF.PEST, 'text': 'Aphids', 'slug': 'aphids'})
        ProblemDataSheet.objects.update_or_create(id=3,    defaults={ 'id': 3,    'type_of': ProblemDataSheet.TYPE_OF.PEST, 'text': 'Caterpillars', 'slug': 'caterpillars'})
        ProblemDataSheet.objects.update_or_create(id=4,    defaults={ 'id': 4,    'type_of': ProblemDataSheet.TYPE_OF.PEST, 'text': 'Codling moth', 'slug': 'codling-moth'})
        ProblemDataSheet.objects.update_or_create(id=5,    defaults={ 'id': 5,    'type_of': ProblemDataSheet.TYPE_OF.PEST, 'text': 'Flea beetles', 'slug': 'flea-beetles'})
        ProblemDataSheet.objects.update_or_create(id=6,    defaults={ 'id': 6,    'type_of': ProblemDataSheet.TYPE_OF.PEST, 'text': 'Thrips', 'slug': 'thrips'})
        ProblemDataSheet.objects.update_or_create(id=7,    defaults={ 'id': 7,    'type_of': ProblemDataSheet.TYPE_OF.PEST, 'text': 'Leaf miners', 'slug': 'leaf-miners'})
        ProblemDataSheet.objects.update_or_create(id=8,    defaults={ 'id': 8,    'type_of': ProblemDataSheet.TYPE_OF.PEST, 'text': 'Mealy bugs', 'slug': 'mealy-bugs'})
        ProblemDataSheet.objects.update_or_create(id=9,    defaults={ 'id': 9,    'type_of': ProblemDataSheet.TYPE_OF.PEST, 'text': 'Mites', 'slug': 'mites'})
        ProblemDataSheet.objects.update_or_create(id=10,   defaults={ 'id': 10,   'type_of': ProblemDataSheet.TYPE_OF.PEST, 'text': 'Scale', 'slug': 'scale'})
        ProblemDataSheet.objects.update_or_create(id=11,   defaults={ 'id': 11,   'type_of': ProblemDataSheet.TYPE_OF.PEST, 'text': 'Vine weevil', 'slug': 'vine-weevil'})
        ProblemDataSheet.objects.update_or_create(id=12,   defaults={ 'id': 12,   'type_of': ProblemDataSheet.TYPE_OF.PEST, 'text': 'Whitefly', 'slug': 'whitefly'})

        #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
        #                            DISEASE PROBLEMS                          #
        #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
        ProblemDataSheet.objects.update_or_create(id=1000, defaults={ 'id': 1000, 'type_of': ProblemDataSheet.TYPE_OF.DISEASE, 'text': 'Anthracnose', 'slug': 'anthracnose'})
        ProblemDataSheet.objects.update_or_create(id=1001, defaults={ 'id': 1001, 'type_of': ProblemDataSheet.TYPE_OF.DISEASE, 'text': 'Leaf spots', 'slug': 'leaf-spots'})
        ProblemDataSheet.objects.update_or_create(id=1002, defaults={ 'id': 1002, 'type_of': ProblemDataSheet.TYPE_OF.DISEASE, 'text': 'Powdery mildew', 'slug': 'powdery-mildew'})
        ProblemDataSheet.objects.update_or_create(id=1003, defaults={ 'id': 1003, 'type_of': ProblemDataSheet.TYPE_OF.DISEASE, 'text': 'Root and stem rots', 'slug': 'root-and-stem-rots'})

        #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
        #                            ABIOTIC PROBLEMS                          #
        #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#
        ProblemDataSheet.objects.update_or_create(id=2000, defaults={ 'id': 2000, 'type_of': ProblemDataSheet.TYPE_OF.ABIOTIC, 'text': 'Spindly plants', 'slug': 'spindly-plants'})
        ProblemDataSheet.objects.update_or_create(id=2001, defaults={ 'id': 2001, 'type_of': ProblemDataSheet.TYPE_OF.ABIOTIC, 'text': 'Few flowers', 'slug': 'few-flowers'})
        ProblemDataSheet.objects.update_or_create(id=2002, defaults={ 'id': 2002, 'type_of': ProblemDataSheet.TYPE_OF.ABIOTIC, 'text': 'Few flowers and excessive growth', 'slug': 'Few-flowers-and-excessive-growth'})
        ProblemDataSheet.objects.update_or_create(id=2003, defaults={ 'id': 2003, 'type_of': ProblemDataSheet.TYPE_OF.ABIOTIC, 'text': 'Yellowing leaves', 'slug': 'yellowing-leaves'})
        ProblemDataSheet.objects.update_or_create(id=2004, defaults={ 'id': 2004, 'type_of': ProblemDataSheet.TYPE_OF.ABIOTIC, 'text': 'Leaves scorched', 'slug': 'leave-scorched'})
        ProblemDataSheet.objects.update_or_create(id=2005, defaults={ 'id': 2005, 'type_of': ProblemDataSheet.TYPE_OF.ABIOTIC, 'text': 'Brown leaf tips', 'slug': 'brown-leaf-tips'})
        ProblemDataSheet.objects.update_or_create(id=2006, defaults={ 'id': 2006, 'type_of': ProblemDataSheet.TYPE_OF.ABIOTIC, 'text': 'Small leaves', 'slug': 'small-leaves'})
        ProblemDataSheet.objects.update_or_create(id=2007, defaults={ 'id': 2007, 'type_of': ProblemDataSheet.TYPE_OF.ABIOTIC, 'text': 'Weak growth', 'slug': 'weak-growth'})
        ProblemDataSheet.objects.update_or_create(id=2008, defaults={ 'id': 2008, 'type_of': ProblemDataSheet.TYPE_OF.ABIOTIC, 'text': 'Wilting plant', 'slug': 'wilting-plant'})
        ProblemDataSheet.objects.update_or_create(id=2009, defaults={ 'id': 2009, 'type_of': ProblemDataSheet.TYPE_OF.ABIOTIC, 'text': 'General defoliation', 'slug': 'general-defoliation'})
