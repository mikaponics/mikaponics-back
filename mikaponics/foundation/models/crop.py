# -*- coding: utf-8 -*-
import uuid
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField


class CropManager(models.Manager):
    def delete_all(self):
        items = Crop.objects.all()
        for item in items.all():
            item.delete()


class Crop(models.Model):
    """
    Class represents a plant, tree fruit or animal product that can be grown
    and harvested extensively for profit or subsistence.
    """

    '''
    Constants & Choices
    '''

    class TYPE_OF:
        PLANT = 1
        ANIMALSTOCK = 2
        FISHSTOCK = 3

    TYPE_OF_CHOICES = (
        (TYPE_OF.PLANT, _('Plant')),
        (TYPE_OF.FISHSTOCK, _('Fishstock')),
    )


    '''
    Metadata
    '''

    class Meta:
        app_label = 'foundation'
        db_table = 'mika_crops'
        verbose_name = _('Crop')
        verbose_name_plural = _('Crop')
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

    objects = CropManager()
    name = models.CharField(
        _("Name"),
        max_length=31,
        help_text=_('The name of the crop.'),
        blank=False,
        null=False,
        unique=True,
        db_index=True,
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of crop being grown in production.'),
        blank=False,
        null=False,
        choices=TYPE_OF_CHOICES,
    )
    order_number = models.PositiveSmallIntegerField(
        _("Order #"),
        help_text=_('The order number to list this crop in.'),
        blank=False,
        null=False,
    )
    stages = JSONField(
        _("Life Cycle Stages"),
        help_text=_('Stages of development this crop has in their lifespan.'),
        blank=False,
        null=False,
    )

    '''
    Method
    '''

    def __str__(self):
        return str(self.name)
