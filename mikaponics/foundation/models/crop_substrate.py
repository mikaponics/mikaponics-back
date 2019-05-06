# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField


class CropSubstrateManager(models.Manager):
    def delete_all(self):
        items = CropSubstrate.objects.all()
        for item in items.all():
            item.delete()


class CropSubstrate(models.Model):
    """
    Class represents the growing medium that the crop can live in.
    """

    '''
    Constants & Choices
    '''

    '''
    Metadata
    '''

    class Meta:
        app_label = 'foundation'
        db_table = 'mika_crop_substrates'
        verbose_name = _('Crop Substrate')
        verbose_name_plural = _('Crop Substrates')
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

    objects = CropSubstrateManager()
    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique slug used for this crop substrate when accessing the details page.'),
        max_length=127,
        blank=True,
        null=False,
        db_index=True,
        unique=True,
    )
    name = models.CharField(
        _("Name"),
        max_length=63,
        help_text=_('The name of the crop substrate.'),
        blank=False,
        null=False,
        unique=True,
        db_index=True,
    )
    order_number = models.PositiveSmallIntegerField(
        _("Order #"),
        help_text=_('The order number to list this crop substrate by.'),
        blank=False,
        null=False,
    )

    def __str__(self):
        return str(self.name)
