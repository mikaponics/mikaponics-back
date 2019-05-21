# -*- coding: utf-8 -*-
import uuid
from django.contrib.postgres.fields import JSONField, DecimalRangeField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField


class CropConditionManager(models.Manager):
    def delete_all(self):
        items = CropCondition.objects.all()
        for item in items.all():
            item.delete()


class CropCondition(models.Model):
    """
    Class represents the optimal growing conditions (ex: ideal pH, EC, etc) for
    a particular crop and the life-cycle stage that crop is at.
    """

    '''
    Constants & Choices
    '''

    class INSTRUMENT_TYPE:
        HUMIDITY = 1
        DAY_AIR_TEMPERATURE = 2
        NIGHT_AIR_TEMPERATURE = 3
        WATER_TEMPERATURE = 4
        TVOC = 5
        CO2 = 6
        AIR_PRESSURE = 7
        ALTITUDE = 8
        PH = 9
        EC = 10
        ORP = 11
        UV_LIGHT = 13

    INSTRUMENT_TYPE_OF_CHOICES = (
        (INSTRUMENT_TYPE.HUMIDITY, _('Humidity')),
        (INSTRUMENT_TYPE.DAY_AIR_TEMPERATURE, _('Day Air Temperature')),
        (INSTRUMENT_TYPE.NIGHT_AIR_TEMPERATURE, _('Night Air Temperature')),
        (INSTRUMENT_TYPE.WATER_TEMPERATURE, _('Water Temperature')),
        (INSTRUMENT_TYPE.TVOC, _('Total Volatile Organic Compound')),
        (INSTRUMENT_TYPE.CO2, _('Carbon Dioxide')),
        (INSTRUMENT_TYPE.AIR_PRESSURE, _('Air Pressure')),
        (INSTRUMENT_TYPE.ALTITUDE, _('Altitude')),
        (INSTRUMENT_TYPE.PH, _('pH')),
        (INSTRUMENT_TYPE.EC, _('Electrical Conductivity')),
        (INSTRUMENT_TYPE.ORP, _('Oxidation-Reduction Potential')),
        (INSTRUMENT_TYPE.UV_LIGHT, _('UV Light')),
    )

    '''
    Metadata
    '''

    class Meta:
        app_label = 'foundation'
        db_table = 'mika_condition'
        verbose_name = _('Crop Condition')
        verbose_name_plural = _('Crop Conditions')
        default_permissions = ()
        permissions = (
        )
        unique_together = ("data_sheet", "stage", 'type_of')
        index_together = ("data_sheet", "stage", 'type_of')

    '''
    Object Manager
    '''

    objects = CropConditionManager()
    data_sheet = models.ForeignKey(
        "CropDataSheet",
        help_text=_('The crop data-sheet this optimal grow condition belongs to.'),
        blank=False,
        null=False,
        related_name="conditions",
        on_delete=models.CASCADE
    )
    stage = models.ForeignKey(
        "CropLifeCycleStage",
        help_text=_('The life cycle stage that this optimal grow condition belongs to.'),
        blank=False,
        null=False,
        related_name="conditions",
        on_delete=models.CASCADE
    )
    type_of = models.PositiveSmallIntegerField(
        _("type of"),
        help_text=_('The type of instrument this is condition belongs to.'),
        blank=False,
        null=False,
        choices=INSTRUMENT_TYPE_OF_CHOICES,
    )

    # --- VALUE --- #
    max_value = models.FloatField(
        _("Max Value"),
        help_text=_('The maximum value this crop can accept for this life-cycle stage.'),
        blank=False,
        null=False,
        validators=[MinValueValidator(0.0), MaxValueValidator(100)],
    )
    min_value = models.FloatField(
        _("Max Value"),
        help_text=_('The minimum value this crop can accept for this life-cycle stage.'),
        blank=False,
        null=False,
        validators=[MinValueValidator(0.0), MaxValueValidator(100)],
    )

    '''
    Method
    '''

    def __str__(self):
        return str(self.id)
