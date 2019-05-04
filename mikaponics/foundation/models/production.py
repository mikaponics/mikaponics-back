# -*- coding: utf-8 -*-
import uuid
import pytz
from faker import Faker
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields import JSONField
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
    The class represents the production of food through a (1) hydroponics
    (2) aquaponics or (3) aquaculture system. Class will track the plants and
    aquatic livestock in the current food production and attach a single
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
        AQUAPONICS = 1
        HYDROPONICS = 2
        AQUACULTURE = 3

    TYPE_OF_CHOICES = (
        (TYPE_OF.AQUAPONICS, _('Aquaponics')),
        (TYPE_OF.HYDROPONICS, _('Hydroponics')),
        (TYPE_OF.AQUACULTURE, _('Aquaculture')),
    )

    class SYSTEM:
        WICK_SYSTEM = 1
        DEEP_WATER_CULTURE_SYSTEM = 2
        EBB_AND_FLOW_SYSTEM = 3
        NFT_SYSTEM = 4 # Nutrient Film Technique
        DRIP_SYSTEM = 5
        AEROPONIC_SYSTEM = 6
        VERTICAL_TOWER_SYSTEM = 7
        OTHER_SYSTEM = 8

    SYSTEM_CHOICES = (
        (SYSTEM.WICK_SYSTEM, _('Wick System')),
        (SYSTEM.DEEP_WATER_CULTURE_SYSTEM, _('Deep Water Culture System')),
        (SYSTEM.EBB_AND_FLOW_SYSTEM, _('Ebb & Flow System')),
        (SYSTEM.NFT_SYSTEM, _('Nutrient Film Technique System')),
        (SYSTEM.DRIP_SYSTEM, _('Drip System')),
        (SYSTEM.AEROPONIC_SYSTEM, _('Aeroponic System')),
        (SYSTEM.VERTICAL_TOWER_SYSTEM, _('Vertical Tower System')),
        (SYSTEM.OTHER_SYSTEM, _('Other (Please specify)')),
    )


    '''
    Object Managers
    '''
    objects = ProductionManager()

    '''
    Fields
    '''

    #
    # Internal Related Fields
    #

    id = models.BigAutoField(
        _("ID"),
        primary_key=True,
    )
    state = models.PositiveSmallIntegerField(
        _("State"),
        help_text=_('The state of coupon.'),
        blank=False,
        null=False,
        default=PRODUCTION_STATE.PREPARING,
        choices=PRODUCTION_STATE_CHOICES,
    )
    previous = models.ForeignKey(
        "self",
        help_text=_('The previous production of food that this production is related to. General this happens with fruit bearing plants / trees.'),
        blank=True,
        null=True,
        related_name="previous_productions",
        on_delete=models.SET_NULL
    )
    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique slug used for this food production when accessing details page.'),
        max_length=127,
        blank=True,
        null=False,
        db_index=True,
        unique=True,
        editable=False,
    )
    device = models.ForeignKey(
        "Device",
        help_text=_('The device which is responsible for monitoring this food production.'),
        blank=False,
        null=False,
        related_name="productions",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        "foundation.User",
        help_text=_('The user whom this food production invoice belongs to.'),
        blank=False,
        null=False,
        related_name="productions",
        on_delete=models.CASCADE
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
    system = models.PositiveSmallIntegerField(
        _("System"),
        help_text=_('The system being used for production.'),
        blank=False,
        null=False,
        choices=SYSTEM_CHOICES,
    )
    system_other = models.CharField(
        _("System (Other)"),
        help_text=_('The description of the other system.'),
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

    #
    # Audit detail fields
    #

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "foundation.User",
        help_text=_('The user whom created this food production.'),
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
        help_text=_('The user whom last modified this food production.'),
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

    def get_pretty_system(self):
        result = dict(self.SYSTEM_CHOICES).get(self.system)
        return str(result)
