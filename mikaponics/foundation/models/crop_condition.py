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

    class OPERATION_CYCLE:
        CONTINUOUS_CYCLE = 1
        DAY_CYCLE = 2
        NIGHT_CYCLE = 3

    OPERATION_CYCLE_CHOICES = (
        (OPERATION_CYCLE.CONTINUOUS_CYCLE, _('Continuous Cycle')),
        (OPERATION_CYCLE.DAY_CYCLE, _('Day Cycle')),
        (OPERATION_CYCLE.NIGHT_CYCLE, _('Night Cycle')),
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
        # unique_together = ("data_sheet", "stage", 'type_of')
        index_together = ("data_sheet", "stage", 'type_of', 'operation_cycle')

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
    operation_cycle = models.PositiveSmallIntegerField(
        _("Operation Cycle"),
        help_text=_('The operation cycle this condition belongs to.'),
        blank=False,
        null=False,
        choices=OPERATION_CYCLE_CHOICES,
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

    def get_pretty_instrument_type_of(self):
        result = dict(self.INSTRUMENT_TYPE_OF_CHOICES).get(self.type_of)
        return str(result)

    def get_transcoded_instrument_type_of(self):
        """
        Function will transcode the `type_id` of this class to the `type_id` of
        the `Instrument` class by transcoding the values.
        """
        from foundation.models.instrument import Instrument

        if self.type_of == CropCondition.INSTRUMENT_TYPE.HUMIDITY:
            return Instrument.INSTRUMENT_TYPE.HUMIDITY

        elif self.type_of == CropCondition.INSTRUMENT_TYPE.DAY_AIR_TEMPERATURE:
            return Instrument.INSTRUMENT_TYPE.AIR_TEMPERATURE

        elif self.type_of == CropCondition.INSTRUMENT_TYPE.NIGHT_AIR_TEMPERATURE:
            return Instrument.INSTRUMENT_TYPE.AIR_TEMPERATURE

        elif self.type_of == CropCondition.INSTRUMENT_TYPE.WATER_TEMPERATURE:
            return Instrument.INSTRUMENT_TYPE.WATER_TEMPERATURE

        elif self.type_of == CropCondition.INSTRUMENT_TYPE.TVOC:
            return Instrument.INSTRUMENT_TYPE.TVOC

        elif self.type_of == CropCondition.INSTRUMENT_TYPE.CO2:
            return Instrument.INSTRUMENT_TYPE.CO2

        elif self.type_of == CropCondition.INSTRUMENT_TYPE.AIR_PRESSURE:
            return Instrument.INSTRUMENT_TYPE.AIR_PRESSURE

        elif self.type_of == CropCondition.INSTRUMENT_TYPE.ALTITUDE:
            return Instrument.INSTRUMENT_TYPE.ALTITUDE

        elif self.type_of == CropCondition.INSTRUMENT_TYPE.PH:
            return Instrument.INSTRUMENT_TYPE.PH

        elif self.type_of == CropCondition.INSTRUMENT_TYPE.EC:
            return Instrument.INSTRUMENT_TYPE.EC

        elif self.type_of == CropCondition.INSTRUMENT_TYPE.ORP:
            return Instrument.INSTRUMENT_TYPE.ORP
        return None
