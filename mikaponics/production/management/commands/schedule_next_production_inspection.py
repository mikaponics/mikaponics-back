# -*- coding: utf-8 -*-
import logging
import os
import sys
from freezegun import freeze_time
from decimal import *
from django.db.models import Sum
from django.db import transaction
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from djmoney.money import Money
from oauthlib.common import generate_token

from foundation.constants import *
from foundation.models import Production, ProductionInspection, TaskItem


class Command(BaseCommand):
    """
    DESCRIPTION:
    Command will process a `Production` and generate a `ProductionInspection` for criteria met.

    EXAMPLE:
    python manage.py schedule_next_production_inspection 1
    """

    help = _('Command generate an inspection if criteria are met for the production.')

    def add_arguments(self, parser):
        parser.add_argument('id', nargs='+', type=int)

    def handle(self, *args, **options):
        utc_today = timezone.now()

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | SNPI | Started running.') % {
                'dt': str(timezone.now())
            })
        )

        try:
            for id in options['id']:
                production = Production.objects.get(id=id)
                self.begin_processing(production)

        except Production.DoesNotExist:
            # For debugging purposes only.
            raise CommandError(_('%(dt)s | SNPI | Production inspeciton does not exist with the id.') % {
                'dt': str(timezone.now())
            })

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | SNPI | Finished running.') % {
                'dt': str(timezone.now())
            })
        )

    def begin_processing(self, production):
        now_dt = timezone.now()
        next_inspection_at = production.next_inspection_at

        if now_dt >= next_inspection_at:
            self.stdout.write(
                self.style.SUCCESS(_('%(dt)s | SNPI | Next inspection at #%(x_dt)s which is ready. Beginning processing...') % {
                    'dt': str(timezone.now()),
                    'x_dt': str(next_inspection_at)
                })
            )
            self.process_production(production)
        else:
            self.stdout.write(
                self.style.SUCCESS(_('%(dt)s | SNPI | Skipping production ID #%(pid)s.') % {
                    'dt': str(timezone.now()),
                    'pid': str(production.id)
                })
            )

    @transaction.atomic
    def process_production(self, production):
        # STEP 1:
        # Create a `TaskItem` object.
        task_item = TaskItem.objects.create(
            user=production.user,
            type_of=TaskItem.TYPE_OF.PRODUCTION_INSPECTION,
            title="test",
            description="test",
            due_date=timezone.now()
        )

        # STEP 2:
        # Create our `ProductionInspection` object.
        production_inspection = ProductionInspection.objects.create(
            production=production,
            state=ProductionInspection.STATE.DRAFT,
            task_item=task_item,
            at_duration=production.get_runtime_duration()
        )

        # STEP 3:
        # Generate relationship between the two.
        task_item.production_inspection = production_inspection
        task_item.save()

        # STEP 4:
        # We need to get the date where the next quality inspection will be created
        next_inspection_at = production.generate_next_inspection_datetime()

        # STEP 5:
        # Update the `Production` object to have the next inspection date in there.
        production.next_inspection_at = next_inspection_at
        production.save()

        # For debugging purposes only.
        self.stdout.write(
            self.style.SUCCESS(_('%(dt)s | SNPI | Created quality inspection task ID #(tid) for production ID #%(pid)s.') % {
                'dt': str(timezone.now()),
                'pid': str(production.id),
                'tid': str(task_item.id)
            })
        )
