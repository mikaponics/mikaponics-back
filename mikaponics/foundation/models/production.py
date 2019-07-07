# -*- coding: utf-8 -*-
import uuid
import pytz
from datetime import datetime
from datetime import timedelta
from faker import Faker
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import BrinIndex
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from oauthlib.common import generate_token
from oauth2_provider.models import (
    Application,
    AbstractApplication,
    AbstractAccessToken,
    AccessToken,
    RefreshToken
)

from foundation.constants import *


class ProductionManager(models.Manager):
    def delete_all(self):
        items = Production.objects.all()
        for item in items.all():
            item.delete()

    # def seed(self, user, product, length=25):
    #     results = []
    #     faker = Faker('en_CA')
    #     for i in range(0,length):
    #         production = Production.objects.create(
    #             name = faker.domain_word(),
    #             description = faker.sentence(nb_words=6, variable_nb_words=True, ext_word_list=None),
    #             user = user,
    #             product = product,
    #         )
    #         results.append(production)
    #     return results


class Production(models.Model):
    """
    The class represents the production of crop through a (1) hydroponics
    (2) aquaponics or (3) aquaculture system. Class will track the plants and
    aquatic livestock in the current crop production and attach a single
    Mikaponics device with it.

    The beginning of a production is defined when a plant has been placed
    as a seed or a previously harvested for their fruits.

    The end of a production is defined as a harvest or termination of the
    plant lifeform.
    """

    '''
    Metadata
    '''
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_productions'
        verbose_name = _('Production')
        verbose_name_plural = _('Productions')
        default_permissions = ()
        permissions = (
            # ("can_get_opening_hours_specifications", "Can get opening hours specifications"),
            # ("can_get_opening_hours_specification", "Can get opening hours specifications"),
            # ("can_post_opening_hours_specification", "Can create opening hours specifications"),
            # ("can_put_opening_hours_specification", "Can update opening hours specifications"),
            # ("can_delete_opening_hours_specification", "Can delete opening hours specifications"),
        )
        indexes = (
            BrinIndex(
                fields=['created_at', 'last_modified_at'],
                autosummarize=True,
            ),
        )

    '''
    Constants & Choices
    '''

    class PRODUCTION_STATE:
        PREPARING = 1
        OPERATING = 3
        TERMINATED = 4

    PRODUCTION_STATE_CHOICES = (
        (PRODUCTION_STATE.PREPARING, _('Preparing')),
        (PRODUCTION_STATE.OPERATING, _('Operating')),
        (PRODUCTION_STATE.TERMINATED, _('Terminated')),
    )

    class ENVIRONMENT:
        INDOOR = 1
        OUTDOOR = 2

    ENVIRONMENT_CHOICES = (
        (ENVIRONMENT.INDOOR, _('Indoor')),
        (ENVIRONMENT.OUTDOOR, _('Outdoor')),
    )

    class TYPE_OF:
        OTHER = 1
        SOIL = 2
        AQUAPONICS = 3
        HYDROPONICS = 4
        AQUACULTURE = 5

    TYPE_OF_CHOICES = (
        (TYPE_OF.SOIL, _('Soil')),
        (TYPE_OF.AQUAPONICS, _('Aquaponics')),
        (TYPE_OF.HYDROPONICS, _('Hydroponics')),
        (TYPE_OF.AQUACULTURE, _('Aquaculture')),
        (TYPE_OF.OTHER, _('Other')),
    )

    class GROW_SYSTEM:
        WICK_SYSTEM = 2
        DEEP_WATER_CULTURE_SYSTEM = 3
        EBB_AND_FLOW_SYSTEM = 4
        NFT_SYSTEM = 5 # Nutrient Film Technique
        DRIP_SYSTEM = 6
        AEROPONIC_SYSTEM = 7
        VERTICAL_TOWER_SYSTEM = 8
        OTHER_SYSTEM = 1

    GROW_SYSTEM_CHOICES = (
        (GROW_SYSTEM.WICK_SYSTEM, _('Wick System')),
        (GROW_SYSTEM.DEEP_WATER_CULTURE_SYSTEM, _('Deep Water Culture System')),
        (GROW_SYSTEM.EBB_AND_FLOW_SYSTEM, _('Ebb & Flow System')),
        (GROW_SYSTEM.NFT_SYSTEM, _('Nutrient Film Technique System')),
        (GROW_SYSTEM.DRIP_SYSTEM, _('Drip System')),
        (GROW_SYSTEM.AEROPONIC_SYSTEM, _('Aeroponic System')),
        (GROW_SYSTEM.VERTICAL_TOWER_SYSTEM, _('Vertical Tower System')),
        (GROW_SYSTEM.OTHER_SYSTEM, _('Other (Please specify)')),
    )

    class ALERT_FREQUENCY_IN_SECONDS:
        EVERY_MINUTE = 60
        EVERY_2_MINUTES = 120
        EVERY_5_MINUTES = 300
        EVERY_10_MINUTES = 600
        EVERY_20_MINUTES = 1200
        EVERY_30_MINUTES = 1800
        EVERY_HOUR = 3600
        EVERY_2_HOURS = 7200
        EVERY_4_HOURS = 14400
        EVERY_6_HOURS = 21600
        EVERY_12_HOURS = 43200
        EVERY_24_HOURS = 86400

    ALERT_FREQUENCY_IN_SECONDS_CHOICES = (
        (ALERT_FREQUENCY_IN_SECONDS.EVERY_MINUTE, _('Every minute')),
        (ALERT_FREQUENCY_IN_SECONDS.EVERY_2_MINUTES, _('Every 2 minutes')),
        (ALERT_FREQUENCY_IN_SECONDS.EVERY_5_MINUTES, _('Every 5 minutes')),
        (ALERT_FREQUENCY_IN_SECONDS.EVERY_10_MINUTES, _('Every 10 minutes')),
        (ALERT_FREQUENCY_IN_SECONDS.EVERY_20_MINUTES, _('Every 20 minutes')),
        (ALERT_FREQUENCY_IN_SECONDS.EVERY_30_MINUTES, _('Every 30 minutes')),
        (ALERT_FREQUENCY_IN_SECONDS.EVERY_HOUR, _('Every hour')),
        (ALERT_FREQUENCY_IN_SECONDS.EVERY_2_HOURS, _('Every 2 hours')),
        (ALERT_FREQUENCY_IN_SECONDS.EVERY_4_HOURS, _('Every 4 hours')),
        (ALERT_FREQUENCY_IN_SECONDS.EVERY_6_HOURS, _('Every 6 hours')),
        (ALERT_FREQUENCY_IN_SECONDS.EVERY_12_HOURS, _('Every 12 hours')),
        (ALERT_FREQUENCY_IN_SECONDS.EVERY_24_HOURS, _('Every 24 hours')),
    )

    class OPERATION_CYCLE:
        CONTINUOUS_CYCLE = 1
        DAY_CYCLE = 2
        NIGHT_CYCLE = 3

    OPERATION_CYCLE_CHOICES = (
        (OPERATION_CYCLE.CONTINUOUS_CYCLE, _('Continuous Cycle')),
        (OPERATION_CYCLE.DAY_CYCLE, _('Day Cycle')),
        (OPERATION_CYCLE.NIGHT_CYCLE, _('Night Cycle')),
    )

    class INSPECTION_FREQUENCY:
        NEVER = 1
        DAILY = 2
        WEEKLY = 3
        BI_WEEKLY = 4
        MONTHLY = 5

    INSPECTION_FREQUENCY_CHOICES = (
        (INSPECTION_FREQUENCY.NEVER, _('Never')),
        (INSPECTION_FREQUENCY.DAILY, _('Daily')),
        (INSPECTION_FREQUENCY.WEEKLY, _('Weekly')),
        (INSPECTION_FREQUENCY.BI_WEEKLY, _('Bi-Weekly')),
        (INSPECTION_FREQUENCY.MONTHLY, _('Monthly')),
    )


    '''
    Object Managers
    '''
    objects = ProductionManager()

    '''
    Fields
    '''

    #
    # Specific production fields.
    #

    id = models.BigAutoField(
        _("ID"),
        primary_key=True,
    )
    state = models.PositiveSmallIntegerField(
        _("State"),
        help_text=_('The state of production.'),
        blank=False,
        null=False,
        default=PRODUCTION_STATE.PREPARING,
        choices=PRODUCTION_STATE_CHOICES,
    )
    previous = models.ForeignKey(
        "self",
        help_text=_('The previous production of crop that this production is related to. General this happens with fruit bearing plants / trees.'),
        blank=True,
        null=True,
        related_name="previous_productions",
        on_delete=models.SET_NULL
    )
    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique slug used for this crop production when accessing details page.'),
        max_length=127,
        blank=True,
        null=False,
        db_index=True,
        unique=True,
        editable=False,
    )
    device = models.ForeignKey(
        "Device",
        help_text=_('The device which is responsible for monitoring this crop production.'),
        blank=False,
        null=False,
        related_name="productions",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        "foundation.User",
        help_text=_('The user whom this crop production invoice belongs to.'),
        blank=False,
        null=False,
        related_name="productions",
        on_delete=models.CASCADE
    )
    has_day_and_night_cycle = models.BooleanField(
        _("Has day/night cycle?"),
        help_text=_('Indicates if this production will have a day/night cycle else this production is a continuous operation.'),
        default=False,
        blank=True,
    )
    day_starts_at = models.TimeField(
        _("Night Start"),
        help_text=_('The start time to the night (dark period).'),
        blank=True,
        null=True,
    )
    day_finishes_at = models.TimeField(
        _("Night Finish"),
        help_text=_('The finish time to the night (dark period).'),
        blank=True,
        null=True,
    )

    #
    # GeoCoordinates (https://schema.org/GeoCoordinates)
    #

    elevation = models.FloatField(
        _("Elevation"),
        help_text=_('The elevation of a location (<a href="https://en.wikipedia.org/wiki/World_Geodetic_System">WGS 84</a>).'),
        blank=True,
        null=True
    )
    location = PointField( # Combine latitude and longitude into a single field.
        _("Location"),
        help_text=_('A longitude and latitude coordinates of this production. For example -81.245277,42.984924 (<a href="https://en.wikipedia.org/wiki/World_Geodetic_System">WGS 84</a>).'),
        null=True,
        blank=True,
        srid=4326,
        db_index=True
    )

    #
    # Thing (https://schema.org/Thing)
    #

    name = models.CharField(
        _("Name"),
        max_length=255,
        help_text=_('The name of the crop production.'),
        blank=False,
        null=False,
    )
    description = models.TextField(
        _("Description"),
        help_text=_('A description of the crop production.'),
        blank=False,
        null=True,
        default='',
    )
    identifier = models.CharField(
        _("Identifier"),
        max_length=255,
        help_text=_('The identifier property represents any kind of identifier for any kind of <a href="https://schema.org/Thing">Thing</a>, such as ISBNs, GTIN codes, UUIDs etc. Schema.org provides dedicated properties for representing many of these, either as textual strings or as URL (URI) links. See <a href="https://schema.org/docs/datamodel.html#identifierBg">background notes</a> for more details.'),
        blank=True,
        null=True,
    )

    #
    # Beginning of Lifecycle Fields
    #

    environment = models.PositiveSmallIntegerField(
        _("Environment"),
        help_text=_('The type of environment the production is taking place in.'),
        blank=False,
        null=False,
        choices=ENVIRONMENT_CHOICES,
    )
    is_commercial = models.BooleanField(
        _("Is for commercial purposes?"),
        help_text=_('Indicates if this production running for commercial purposes or not.'),
        default=False,
        blank=True,
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of production.'),
        blank=False,
        null=False,
        choices=TYPE_OF_CHOICES,
    )
    type_of_other = models.CharField(
        _("Type of (Other)"),
        help_text=_('The details of the other type of.'),
        blank=True,
        null=True,
        max_length=63,
    )
    grow_system = models.PositiveSmallIntegerField(
        _("Grow System"),
        help_text=_('The growth system being used for crop production.'),
        blank=False,
        null=False,
        choices=GROW_SYSTEM_CHOICES,
    )
    grow_system_other = models.CharField(
        _("Grow System (Other)"),
        help_text=_('The description of the other growth system.'),
        blank=True,
        null=True,
        max_length=63,
    )
    started_at = models.DateTimeField(
        _("Started at"),
        help_text=_('The date/time this production started.'),
        blank=True,
        null=True,
    )


    #
    # End of Lifecycle Fields
    #

    finished_at = models.DateTimeField(
        _("Finished at"),
        help_text=_('The date/time this production finished.'),
        blank=True,
        null=True,
    )
    was_success = models.NullBooleanField(
        _("Was this crop production a success upon completion?"),
        help_text=_('Indicates if this crop production was considered a success to the user or a failure.'),
        default=None,
        blank=True,
    )
    failure_reason = models.TextField(
        _("Failure Reason"),
        help_text=_('The reason why this crop production was overall considered a failure by the user.'),
        blank=True,
        null=True,
    )
    notes = models.TextField(
        _("Comments"),
        help_text=_('Any notes to add upon the completion or operation of the production.'),
        blank=True,
        null=True,
    )

    #
    # Evaluation Fields
    #

    evaluation_score = models.FloatField(
        _("Evaluation"),
        help_text=_('The evaluation score of the current production in the current present date and time.'),
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100)],
    )
    evaluation_has_error = models.BooleanField(
        _("Evaluation has Error?"),
        help_text=_('Indicates if there was an error with the evaluation or not.'),
        default=False,
        blank=True,
        editable=False,
    )
    evaluated_at = models.DateTimeField(
        _("Evaluated At"),
        help_text=_('The datetime of the when the evaluation was done.'),
        blank=True,
        null=True,
    )

    #
    # Alarm configuration.
    #

    yellow_below_value = models.FloatField(
        _("Yellow below value"),
        help_text=_('The value that if is less then or equal to then our system will trigger a yellow alert.'),
        blank=True,
        null=True,
    )
    orange_below_value = models.FloatField(
        _("Orange below value"),
        help_text=_('The value that if is less then or equal to then our system will trigger a orange alert.'),
        blank=True,
        null=True,
    )
    red_below_value = models.FloatField(
        _("Red below value"),
        help_text=_('The value that if is less then or equal to then our system will trigger a red alert.'),
        blank=True,
        null=True,
    )
    red_alert_delay_in_seconds = models.PositiveIntegerField(
        _("Red alert delay (seconds)"),
        help_text=_('The time that red alerts will be sent from the last time the red alert was sent.'),
        blank=True,
        null=True,
        default=ALERT_FREQUENCY_IN_SECONDS.EVERY_MINUTE,
        choices=ALERT_FREQUENCY_IN_SECONDS_CHOICES,
    )
    orange_alert_delay_in_seconds = models.PositiveIntegerField(
        _("Orange alert delay (seconds)"),
        help_text=_('The time that orange alerts will be sent from the last time the orange alert was sent.'),
        blank=True,
        null=True,
        default=ALERT_FREQUENCY_IN_SECONDS.EVERY_MINUTE,
        choices=ALERT_FREQUENCY_IN_SECONDS_CHOICES,
    )
    yellow_alert_delay_in_seconds = models.PositiveIntegerField(
        _("Yellow alert delay (seconds)"),
        help_text=_('The time that yellow alerts will be sent from the last time the yellow alert was sent.'),
        blank=True,
        null=True,
        default=ALERT_FREQUENCY_IN_SECONDS.EVERY_MINUTE,
        choices=ALERT_FREQUENCY_IN_SECONDS_CHOICES,
    )

    #
    # PRODUCTION INSPECTION REMINDER TASK FIELDS
    #

    inspections_start_at = models.DateTimeField(
        _("Inspections start at"),
        help_text=_('The date/time this production\'s inspections will start.'),
        blank=True,
        null=True,
    )
    inspection_frequency = models.PositiveIntegerField(
        _("Inspections frequency"),
        help_text=_('The frequency to create `production inspection` tasks.'),
        blank=True,
        null=False,
        default=INSPECTION_FREQUENCY.WEEKLY,
        choices=INSPECTION_FREQUENCY_CHOICES,
    )
    next_inspection_at = models.DateTimeField(
        _('Next inspection at'),
        help_text=_('The date and time of the next scheduled inspection.'),
        blank=True,
        null=True
    )

    #
    # Audit detail fields
    #

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "foundation.User",
        help_text=_('The user whom created this crop production.'),
        related_name="created_productions",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        editable=False,
    )
    created_from = models.GenericIPAddressField(
        _("Created from IP"),
        help_text=_('The IP address of the creator.'),
        blank=True,
        null=True,
        editable=False,
    )
    created_from_is_public = models.BooleanField(
        _("Is created from IP public?"),
        help_text=_('Is creator a public IP and is routable.'),
        default=False,
        blank=True,
        editable=False,
    )
    last_modified_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        "foundation.User",
        help_text=_('The user whom last modified this crop production.'),
        related_name="last_modified_productions",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        editable=False,
    )
    last_modified_from = models.GenericIPAddressField(
        _("Last modified from IP"),
        help_text=_('The IP address of the modifier.'),
        blank=True,
        null=True,
        editable=False,
    )
    last_modified_from_is_public = models.BooleanField(
        _("Is Last modified from IP public?"),
        help_text=_('Is modifier a public IP and is routable.'),
        default=False,
        blank=True,
        editable=False,
    )

    def save(self, *args, **kwargs):
        """
        Override the save function so we can add extra functionality.

        (1) If we created the object then we will generate a custom slug.
        (a) If user exists then generate slug based on user's name.
        (b) Else generate slug with random string.
        """
        if not self.slug:
            # CASE 1 OF 2: HAS USER.
            if self.user:
                count = Production.objects.filter(user=self.user).count()
                count += 1

                # Generate our slug.
                self.slug = slugify(self.user)+"-production-"+str(count)

                # If a unique slug was not found then we will keep searching
                # through the various slugs until a unique slug is found.
                while Production.objects.filter(slug=self.slug).exists():
                    self.slug = slugify(self.user)+"-production-"+str(count)+"-"+get_random_string(length=8)

            # CASE 2 OF 2: DOES NOT HAVE USER.
            else:
                self.slug = "production-"+get_random_string(length=32)

        super(Production, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.slug)

    def get_pretty_state(self):
        result = dict(self.PRODUCTION_STATE_CHOICES).get(self.state)
        return str(result)

    def get_pretty_environment(self):
        result = dict(self.ENVIRONMENT_CHOICES).get(self.environment)
        return str(result)

    def get_pretty_type_of(self):
        result = dict(self.TYPE_OF_CHOICES).get(self.type_of)
        return str(result)

    def get_pretty_grow_system(self):
        result = dict(self.GROW_SYSTEM_CHOICES).get(self.grow_system)
        return str(result)

    def get_pretty_last_modified_at(self):
        return str(self.last_modified_at)

    def get_absolute_url(self):
        return "/production/"+self.slug

    def get_evaluation_letter(self):
        if self.evaluation_has_error:
            return "Has error"
        if self.evaluation_score is None:
            return "Not evaluated yet"
        if self.evaluation_score < 50:
            return "F"
        elif self.evaluation_score >= 50 and self.evaluation_score < 60:
            return "D"
        elif self.evaluation_score >= 60 and self.evaluation_score < 70:
            return "C"
        elif self.evaluation_score >= 70 and self.evaluation_score < 80:
            return "B"
        elif self.evaluation_score >= 80 and self.evaluation_score < 90:
            return "A"
        elif self.evaluation_score >= 90:
            return "A+"

    def get_alert_condition(self):
        from foundation.models.alert_item import AlertItem
        if self.evaluation_score:
            if self.red_below_value:
                if self.evaluation_score <= self.red_below_value:
                    return AlertItem.ALERT_ITEM_CONDITION.RED_BELOW_VALUE
            if self.orange_below_value:
                if self.evaluation_score <= self.orange_below_value:
                    return AlertItem.ALERT_ITEM_CONDITION.ORANGE_BELOW_VALUE
            if self.yellow_below_value:
                if self.evaluation_score <= self.yellow_below_value:
                    return AlertItem.ALERT_ITEM_CONDITION.YELLOW_BELOW_VALUE
        return None

    def get_runtime_duration(self):
        """
        Function returns the python `timedelta` of either:
        (1) Start date to current date
        (2) Start date to finish date
        """
        aware_start_dt = self.started_at
        if self.finished_at:
            time_difference = self.finished_at - aware_start_dt
            time_difference_in_minutes = time_difference / timedelta(minutes=1)
            return timedelta(minutes=time_difference_in_minutes)
        else:
            utc_today = timezone.now()
            time_difference = utc_today - aware_start_dt
            time_difference_in_minutes = time_difference / timedelta(minutes=1)
            return timedelta(minutes=time_difference_in_minutes)

    def get_operation_cycle(self):
        """
        Function will return an indication of whether this production is in
        (1) continuous (2) day or (3) night operation cycle.
        """
        # STEP 1:
        # Check to see if the night has been set, if not then return the
        # continuous cycle.
        if self.has_day_and_night_cycle is False:
            return self.OPERATION_CYCLE.CONTINUOUS_CYCLE

        # STEP 2:
        # Get the timezone aware python `datetime` object of the user's time.
        aware_dt = self.user.get_now()

        # print(aware_dt.time())
        # print(self.day_starts_at)
        # print(self.day_finishes_at)

        # STEP 3:
        # Check the time of the current time and if it is within the specified
        # night start and finish time then return the night cycle status, else
        # return the day cycle status.
        if aware_dt.time() >= self.day_starts_at:
            if aware_dt.time() <= self.day_finishes_at:
                return self.OPERATION_CYCLE.DAY_CYCLE
        return self.OPERATION_CYCLE.NIGHT_CYCLE

    def get_pretty_operation_cycle(self):
        operation_cycle = self.get_operation_cycle()
        result = dict(self.OPERATION_CYCLE_CHOICES).get(operation_cycle)
        return str(result)

    def get_pretty_inspection_frequency(self):
        result = dict(self.INSPECTION_FREQUENCY_CHOICES).get(self.inspection_frequency)
        return str(result)

    def generate_next_inspection_datetime(self):
        if self.inspection_frequency == self.INSPECTION_FREQUENCY.NEVER:
            return None
        now_dt = self.inspections_start_at if self.next_inspection_at is None else self.next_inspection_at
        if self.inspection_frequency == self.INSPECTION_FREQUENCY.DAILY:
            return now_dt + timedelta(hours=24)
        elif self.inspection_frequency == self.INSPECTION_FREQUENCY.WEEKLY:
            return now_dt + timedelta(days=7)
        elif self.inspection_frequency == self.INSPECTION_FREQUENCY.BI_WEEKLY:
            return now_dt + timedelta(days=14)
        elif self.inspection_frequency == self.INSPECTION_FREQUENCY.MONTHLY:
            return now_dt + timedelta(days=30)
        return None
