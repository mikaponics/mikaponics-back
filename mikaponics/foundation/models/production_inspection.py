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


class ProductionInspection(models.Model):
    """
    Class represents a single quality assurance inspection of the production
    sytem (ie. hydropnics system) in a point in date and time.
    """

    '''
    Metadata
    '''
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_production_inspections'
        verbose_name = _('Production Inspection')
        verbose_name_plural = _('Production Inspections')
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

    production = models.ForeignKey(
        "Production",
        verbose_name=_('Production'),
        help_text=_("The crop production we are inspecting."),
        blank=False,
        null=False,
        related_name="inspections",
        on_delete=models.CASCADE
    )
    did_pass = models.NullBooleanField(
        _("Did pass?"),
        help_text=_('Indicates if the evaulation of the system resulted in a passing score.'),
        default=None,
        blank=True,
    )
    failure_reason = models.TextField(
        _("Failure Reason"),
        help_text=_('The reason why this inspection was considered a failure during inspection.'),
        blank=True,
        null=True,
    )
    notes = models.TextField(
        _("Notes"),
        help_text=_('Any notes for this crop production inspection.'),
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
        related_name="created_production_inspections",
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
        related_name="last_modified_production_inspections",
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
            count = ProductionInspection.objects.filter(created_by=self.created_by).count()
            count += 1

            # Generate our slug.
            self.slug = self.production.slug+"-inspection-"+str(count)

            # If a unique slug was not found then we will keep searching
            # through the various slugs until a unique slug is found.
            while ProductionInspection.objects.filter(slug=self.slug).exists():
                self.slug = sself.production.slug+"-inspection-"+str(count)+"-"+get_random_string(length=16)

        super(ProductionInspection, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.slug)

    def get_pretty_state(self):
        result = dict(self.STATE_CHOICES).get(self.state)
        return str(result)

    def get_absolute_url(self):
        if self.state == ProductionInspection.STATE.DRAFT:
            return "/production/"+self.production.slug+"/create-inspection/start"
        else:
            return "/production-inspection/"+self.slug
