# -*- coding: utf-8 -*-
import uuid
import pytz
from faker import Faker
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import BrinIndex
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


class ProductionCropInspectionManager(models.Manager):
    def delete_all(self):
        items = ProductionCropInspection.objects.all()
        for item in items.all():
            item.delete()

    # def seed(self, user, product, length=25):
    #     results = []
    #     faker = Faker('en_CA')
    #     for i in range(0,length):
    #         farm = ProductionCropInspection.objects.create(
    #             name = faker.domain_word(),
    #             description = faker.sentence(nb_words=6, variable_nb_words=True, ext_word_list=None),
    #             user = user,
    #             product = product,
    #         )
    #         results.append(farm)
    #     return results


class ProductionCropInspection(models.Model):
    """
    Class represents a single quality assurance inspection of a crop in a point
    in date and time within a system.
    """

    '''
    Metadata
    '''
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_production_crop_inspections'
        verbose_name = _('Production Crop Inspection')
        verbose_name_plural = _('Production Crop Inspections')
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

    class REVIEW:
        TERRIBLE = 1
        BAD = 2
        AVERAGE = 3
        GOOD = 4
        EXCELLENT = 5

    REVIEW_CHOICES = (
        (REVIEW.EXCELLENT, _('Excellent')),
        (REVIEW.GOOD, _('Bad')),
        (REVIEW.AVERAGE, _('Average')),
        (REVIEW.BAD, _('Good')),
        (REVIEW.TERRIBLE, _('Excellent')),
    )

    class STATE:
        DRAFT = 1
        SUBMITTED = 2

    STATE_CHOICES = (
        (STATE.DRAFT, _('Draft')),
        (STATE.SUBMITTED, _('Submitted')),
    )

    '''
    Object Managers
    '''
    objects = ProductionCropInspectionManager()

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
        help_text=_('The unique slug used for this crop production inspection when accessing details page.'),
        max_length=511,
        blank=True,
        null=False,
        db_index=True,
        unique=True,
        editable=False,
    )
    state = models.PositiveSmallIntegerField(
        _("State"),
        help_text=_('The state of inspection.'),
        blank=False,
        null=False,
        default=STATE.DRAFT,
        choices=STATE_CHOICES,
    )

    #
    # Quality Assurance Inspection Fields
    #

    production_inspection = models.ForeignKey(
        "ProductionInspection",
        verbose_name=_('Production Inspection'),
        help_text=_("The production we are evaluating for this quality assurance crop inspection."),
        blank=False,
        null=False,
        related_name="crop_inspections",
        on_delete=models.CASCADE
    )
    production_crop = models.ForeignKey(
        "ProductionCrop",
        verbose_name=_('Production Crop'),
        help_text=_("The plants or fish that we are evaluating for this quality assurance inspection."),
        blank=False,
        null=False,
        related_name="inspections",
        on_delete=models.CASCADE
    )
    review = models.PositiveSmallIntegerField(
        _("Review"),
        help_text=_('The review of the user for this crop at this time.'),
        blank=True,
        null=True,
        choices=REVIEW_CHOICES,
    )
    failure_reason = models.TextField(
        _("Failure Reason"),
        help_text=_('The reason why this crop inspection was considered a failure during inspection.'),
        blank=True,
        null=True,
    )
    stage = models.PositiveSmallIntegerField(
        _("Life Cycle Stage"),
        help_text=_('The observed stage in the life cycle by the user.'),
        blank=True,
        null=True,
    )
    notes = models.TextField(
        _("Notes"),
        help_text=_('Any notes for this inspection.'),
        blank=True,
        null=True,
    )


    #
    # Audit detail fields
    #

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "foundation.User",
        help_text=_('The user whom created this crop production inspections.'),
        related_name="created_production_crop_inspections",
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
        help_text=_('The user whom last modified this crop production inspection.'),
        related_name="last_modified_production_crop_inspections",
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
            count = ProductionCropInspection.objects.filter(
                production_inspection=self.production_inspection
            ).count()
            count += 1

            # Generate our slug.
            self.slug = self.production_inspection.slug+"-crop-"+str(count)

            # If a unique slug was not found then we will keep searching
            # through the various slugs until a unique slug is found.
            while ProductionCropInspection.objects.filter(slug=self.slug).exists():
                self.slug = self.production_inspection.slug+"-crop-"+str(count)+"-"+get_random_string(length=16)

        super(ProductionCropInspection, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.slug)

    def get_pretty_state(self):
        result = dict(self.STATE_CHOICES).get(self.state)
        return str(result)

    def get_pretty_review(self):
        result = dict(self.REVIEW_CHOICES).get(self.review)
        return str(result)

    def get_pretty_stage(self):
        if self.production_crop:
            if self.production_crop.crop:
                stages = self.production_crop.crop.stages
                for stage in stages:
                    if stage['id'] == self.stage:
                        return stage['value'];
        return None

    def get_absolute_url(self):
        return "/production-crop-inspection/"+self.slug
