# -*- coding: utf-8 -*-
import uuid
from django.contrib.postgres.fields import JSONField, DecimalRangeField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField


class CropLifeCycleStageManager(models.Manager):
    def delete_all(self):
        items = CropLifeCycleStage.objects.all()
        for item in items.all():
            item.delete()


class CropLifeCycleStage(models.Model):
    """
    Class represents a stage in the life cycle of a crop. For example:
    Growing, Flowering, Seeding, etc.
    """

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


    '''
    Metadata
    '''

    class Meta:
        app_label = 'foundation'
        db_table = 'mika_crop_life_cycle_stages'
        verbose_name = _('Crop Life Cycle Stage')
        verbose_name_plural = _('Crop Life Cycle Stages')
        default_permissions = ()
        permissions = (
            # ("can_get_opening_hours_specifications", "Can get opening hours specifications"),
            # ("can_get_opening_hours_specification", "Can get opening hours specifications"),
            # ("can_post_opening_hours_specification", "Can create opening hours specifications"),
            # ("can_put_opening_hours_specification", "Can update opening hours specifications"),
            # ("can_delete_opening_hours_specification", "Can delete opening hours specifications"),
        )

    '''
    Object Manager
    '''

    objects = CropLifeCycleStageManager()
    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique slug used for this stage when accessing the details page.'),
        max_length=255,
        blank=True,
        null=False,
        db_index=True,
        unique=True,
    )
    name = models.CharField(
        _("Name"),
        max_length=63,
        help_text=_('The name of the stage.'),
        blank=False,
        null=False,
        unique=True,
        db_index=True,
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of crop this stage belongs to.'),
        blank=False,
        null=False,
        choices=TYPE_OF_CHOICES,
    )
    order_number = models.PositiveSmallIntegerField(
        _("Order #"),
        help_text=_('The order number to list this stage in.'),
        blank=False,
        null=False,
    )


    '''
    Method
    '''

    def __str__(self):
        return str(self.name)
