# -*- coding: utf-8 -*-
import uuid
import pytz
from faker import Faker
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db.models import PointField
from django.contrib.postgres.indexes import BrinIndex
from django.contrib.postgres.fields import JSONField
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

    class TYPE_OF:
        PLANT = 1
        FISHSTOCK = 2
        ANIMALSTOCK = 3
        NONE = 0

    TYPE_OF_CHOICES = (
        (TYPE_OF.PLANT, _('Plant')),
        (TYPE_OF.FISHSTOCK, _('Fishstock')),
        (TYPE_OF.ANIMALSTOCK, _('Animalstock')),
        (TYPE_OF.NONE, _('None')),
    )

    class HARVEST_FAILURE_REASON:
        OTHER_PROBLEM = 1
        PEST_PROBLEM = 2
        DISEASE_PROBLEM = 3
        ABIOTIC_PROBLEM = 4
        TECHNICAL_FAILURE = 5
        HUMAN_ERROR = 6

    HARVEST_FAILURE_REASON_CHOICES = (
        (HARVEST_FAILURE_REASON.PEST_PROBLEM, _('Pest Problem')),
        (HARVEST_FAILURE_REASON.DISEASE_PROBLEM, _('Disease Problem')),
        (HARVEST_FAILURE_REASON.ABIOTIC_PROBLEM, _('Abiotic Problem')),
        (HARVEST_FAILURE_REASON.TECHNICAL_FAILURE, _('Technical Problem')),
        (HARVEST_FAILURE_REASON.HUMAN_ERROR, _('Human Error')),
        (HARVEST_FAILURE_REASON.OTHER_PROBLEM, _('Other')),
    )

    class HARVEST_RATING:
        TERRIBLE = 1
        BAD = 2
        AVERAGE = 3
        GOOD = 4
        EXCELLENT = 5

    HARVEST_RATING_CHOICES = (
        (HARVEST_RATING.EXCELLENT, _('Excellent')),
        (HARVEST_RATING.GOOD, _('Bad')),
        (HARVEST_RATING.AVERAGE, _('Average')),
        (HARVEST_RATING.BAD, _('Good')),
        (HARVEST_RATING.TERRIBLE, _('Excellent')),
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
    data_sheet = models.ForeignKey(
        "CropDataSheet",
        verbose_name=_('CropDataSheet'),
        help_text=_("The plants or fish that we are growing in production."),
        blank=False,
        null=False,
        related_name="production_crops",
        on_delete=models.CASCADE,
    )
    data_sheet_other = models.CharField(
        _("Crop Data Sheet (Other)"),
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
    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of production crop.'),
        blank=False,
        null=False,
        choices=TYPE_OF_CHOICES,
    )

    #
    # At Finish Fields
    #
    stage = models.ForeignKey(
        "CropLifeCycleStage",
        verbose_name=_('Stage'),
        help_text=_("The current stge of the life-cycle that this crop is at."),
        blank=False,
        null=False,
        related_name="production_crops",
        on_delete=models.CASCADE,
    )
    was_harvested = models.NullBooleanField(
        _("Was this crop production harvseted?"),
        help_text=_('Indicates if this crop production was harvested or not.'),
        default=None,
        blank=True,
    )
    harvest_failure_reason = models.PositiveSmallIntegerField(
        verbose_name=_('Harvest Failure Reason'),
        help_text=_('The reason why this crop production was not harvested.'),
        blank=True,
        null=True,
        choices=HARVEST_FAILURE_REASON_CHOICES,
    )
    harvest_failure_reason_other = models.CharField(
        _("Harvest Failure Reason (Other)"),
        help_text=_('A reason why the harvest failed that our system does not know.'),
        blank=True,
        null=True,
        max_length=255,
    )
    harvest_yield = models.PositiveSmallIntegerField(
        verbose_name=_('Harvest yield'),
        help_text=_('The harvest yield rating when the crop production has finished.'),
        blank=True,
        null=True,
        choices=HARVEST_RATING_CHOICES,
    )
    harvest_quality = models.PositiveSmallIntegerField(
        verbose_name=_('Harvest quality'),
        help_text=_('The harvest quality rating when the crop production has finished.'),
        blank=True,
        null=True,
        choices=HARVEST_RATING_CHOICES,
    )
    harvest_notes = models.TextField(
        _("Harvest notes"),
        help_text=_('Any notes or notes of the harvest when the crop production has finished or during operation.'),
        blank=True,
        null=True,
    )
    harvest_weight = models.FloatField(
        verbose_name=_('Harvest weight'),
        help_text=_('The harvest weight at completion.'),
        blank=True,
        null=True,
    )
    harvest_weight_unit = models.CharField(
        _("Harvest weight unit of measure"),
        help_text=_('The harvest weight unit of measure at completion.'),
        blank=True,
        null=True,
        max_length=15,
    )
    average_length = models.FloatField(
        verbose_name=_('Average Length'),
        help_text=_('The average length of the production crop at completion.'),
        blank=True,
        null=True,
    )
    average_width = models.FloatField(
        verbose_name=_('Average Width'),
        help_text=_('The average wdith of the production crop at completion.'),
        blank=True,
        null=True,
    )
    average_height = models.FloatField(
        verbose_name=_('Average Height'),
        help_text=_('The average height of the production crop at completion.'),
        blank=True,
        null=True,
    )
    was_alive_after_harvest = models.NullBooleanField(
        _("Was alive after harvest?"),
        help_text=_('Indicates if this `crop` organism was considered alive when harvested or not.'),
        default=None,
        blank=True,
    )
    notes = models.TextField(
        _("Note(s) / Comment(s)"),
        help_text=_('Any notes or notes of the crop when the production has finished.'),
        blank=True,
        null=True,
    )

    #
    # Evaluation Fields
    #

    evaluation_score = models.FloatField(
        _("Evaluation Score"),
        help_text=_('The evaluation score of the current crop in the current present date and time.'),
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100)],
    )
    evaluation_error = models.CharField(
        _("Evaluation Error"),
        help_text=_('The evaluation error message explaining why the evaluation could not be computed.'),
        blank=True,
        null=True,
        max_length=255,
    )
    evaluation_passes = JSONField(
        _("Evaluation Pass(es)"),
        help_text=_('The dictionary of instrument slugs which passed the evaluation.'),
        blank=True,
        null=True,
        max_length=127,
    )
    evaluation_failures = JSONField(
        _("Evaluation Failure(s)"),
        help_text=_('The dictionary of instrument slugs and the condition failed for the instrument in the computed evaluation.'),
        blank=True,
        null=True,
        max_length=255,
    )
    evaluated_at = models.DateTimeField(
        _("Evaluated At"),
        help_text=_('The datetime of the when the evaluation was done.'),
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
        if self.data_sheet_other:
            return self.data_sheet_other
        else:
            return self.data_sheet.name

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

    def get_evaluation_letter(self):
        if self.evaluation_error:
            return self.evaluation_error
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
