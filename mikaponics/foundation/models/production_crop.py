# -*- coding: utf-8 -*-
import uuid
import pytz
from faker import Faker
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db.models import PointField
from django.contrib.postgres.indexes import BrinIndex
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


class ProductionCropManager(models.Manager):
    def delete_all(self):
        items = ProductionCrop.objects.all()
        for item in items.all():
            item.delete()

    # def seed(self, user, product, length=25):
    #     results = []
    #     faker = Faker('en_CA')
    #     for i in range(0,length):
    #         farm = ProductionCrop.objects.create(
    #             name = faker.domain_word(),
    #             description = faker.sentence(nb_words=6, variable_nb_words=True, ext_word_list=None),
    #             user = user,
    #             product = product,
    #         )
    #         results.append(farm)
    #     return results


class ProductionCrop(models.Model):
    """
    Class represents a crop which is currently being grown in production.
    """

    '''
    Metadata
    '''
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_production_crops'
        verbose_name = _('Production Crop')
        verbose_name_plural = _('Production Crops')
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

    class CROP_STATE_AT_FINISH:
        CROPS_DIED = 1
        CROPS_WERE_ALIVE = 2
        CROPS_WERE_ALIVE_WITH_HARVEST = 3
        CROPS_WERE_TERMINATED = 4
        CROPS_WERE_TERMINATED_WITH_HARVEST = 5

    CROP_STATE_AT_FINISH_CHOICES = (
        (CROP_STATE_AT_FINISH.CROPS_DIED, _('Crops died')),
        (CROP_STATE_AT_FINISH.CROPS_WERE_ALIVE, _('Crops were alive')),
        (CROP_STATE_AT_FINISH.CROPS_WERE_ALIVE_WITH_HARVEST, _('Crops were alive at harvest')),
        (CROP_STATE_AT_FINISH.CROPS_WERE_TERMINATED, _('Crops were terminated')),
        (CROP_STATE_AT_FINISH.CROPS_WERE_TERMINATED_WITH_HARVEST, _('Crops were terminated with harvest')),
    )

    class HARVEST_REVIEW:
        TERRIBLE = 1
        BAD = 2
        AVERAGE = 3
        GOOD = 4
        EXCELLENT = 5

    HARVEST_REVIEW_CHOICES = (
        (HARVEST_REVIEW.EXCELLENT, _('Excellent')),
        (HARVEST_REVIEW.GOOD, _('Bad')),
        (HARVEST_REVIEW.AVERAGE, _('Average')),
        (HARVEST_REVIEW.BAD, _('Good')),
        (HARVEST_REVIEW.TERRIBLE, _('Excellent')),
    )


    '''
    Object Managers
    '''
    objects = ProductionCropManager()

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
    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique slug used for this crop when accessing details page.'),
        max_length=127,
        blank=True,
        null=False,
        db_index=True,
        unique=True,
        editable=False,
    )

    #
    # Core Fields
    #

    production = models.ForeignKey(
        "Production",
        verbose_name=_('Production'),
        help_text=_("The production this crop belongs to."),
        blank=False,
        null=False,
        related_name="crops",
        on_delete=models.CASCADE,
    )
    crop = models.ForeignKey(
        "Crop",
        verbose_name=_('Crop'),
        help_text=_("The plants or fish that we are growing in production."),
        blank=False,
        null=False,
        related_name="production_crops",
        on_delete=models.CASCADE,
    )
    crop_other = models.CharField(
        _("Crop (Other)"),
        help_text=_('The name of crop the user is producing in production that is not in our system.'),
        blank=True,
        null=True,
        max_length=255,
    )
    quantity = models.PositiveSmallIntegerField(
        verbose_name=_('Quantity'),
        help_text=_('The quantity of plants or fish that are being produced.'),
        blank=False,
        null=False
    )
    substrate = models.ForeignKey(
        "CropSubstrate",
        help_text=_('The growing medium used for this plant/fish in production.'),
        blank=True,
        null=True,
        related_name="production_crops",
        on_delete=models.SET_NULL
    )
    substrate_other = models.CharField(
        _("Substrate (Other)"),
        help_text=_('The name of the substrate the user is using which we do not have in our system.'),
        blank=True,
        null=True,
        max_length=255,
    )
    state_at_finish = models.PositiveSmallIntegerField(
        verbose_name=_('State at finish'),
        help_text=_('The state of the crop when the production has finished.'),
        blank=True,
        null=True,
        choices=CROP_STATE_AT_FINISH_CHOICES,
    )
    state_failure_reason_at_finish = models.TextField(
        _("Failure reason at finish"),
        help_text=_('Th failure reason of the crop when the production has finished.'),
        blank=True,
        null=True,
    )
    notes_at_finish = models.TextField(
        _("Comments at finish"),
        help_text=_('Any notes or notes of the crop when the production has finished.'),
        blank=True,
        null=True,
    )
    harvest_at_finish = models.PositiveSmallIntegerField(
        verbose_name=_('Harvest review at finish'),
        help_text=_('The harvest review made by the user when the production has finished.'),
        blank=True,
        null=True,
        choices=HARVEST_REVIEW_CHOICES,
    )
    harvest_failure_reason_at_finish = models.TextField(
        _("Harvest failure at finish"),
        help_text=_('The harvest failure reason of the crop when the production has finished.'),
        blank=True,
        null=True,
    )
    harvest_notes_at_finish = models.TextField(
        _("Harvest notes at finish"),
        help_text=_('Any notes or notes of the harvest when the production has finished.'),
        blank=True,
        null=True,
    )


    #
    # Audit detail fields
    #

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "foundation.User",
        help_text=_('The user whom created this food production inspections.'),
        related_name="created_production_crops",
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
        help_text=_('The user whom last modified this food production inspection.'),
        related_name="last_modified_production_crops",
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

    '''
    Methods
    '''

    def save(self, *args, **kwargs):
        """
        Override the save function so we can add extra functionality.

        (1) If we created the object then we will generate a custom slug.
        (a) If user exists then generate slug based on user's name.
        (b) Else generate slug with random string.
        """
        if not self.slug:
            # CASE 1 OF 2: HAS USER.
            if self.production.user:
                count = ProductionCrop.objects.filter(production__user=self.production.user).count()
                count += 1

                # Generate our slug.
                self.slug = self.production.slug+"-crop-"+str(count)

                # If a unique slug was not found then we will keep searching
                # through the various slugs until a unique slug is found.
                while ProductionCrop.objects.filter(slug=self.slug).exists():
                    self.slug = self.production.slug+"-crop-"+str(count)+"-"+get_random_string(length=8)

            # CASE 2 OF 2: DOES NOT HAVE USER.
            else:
                self.slug = self.production.slug+"-crop-"+get_random_string(length=32)

        super(ProductionCrop, self).save(*args, **kwargs)

    def get_pretty_name(self):
        if self.crop_other:
            return self.crop_other
        else:
            return self.crop.name

    def get_pretty_substrate_name(self):
        if self.substrate_other:
            return self.substrate_other
        else:
            return str(self.substrate.name)

    def get_pretty_state_at_finish(self):
        result = dict(self.CROP_STATE_AT_FINISH_CHOICES).get(self.state_at_finish)
        return str(result)

    def __str__(self):
        return str(self.slug)

    def get_absolute_url(self):
        return "/production-crop/"+self.slug
