# -*- coding: utf-8 -*-
import pytz
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class InstrumentAnalysisManager(models.Manager):
    def delete_all(self):
        items = InstrumentAnalysis.objects.all()
        for item in items.all():
            item.delete()


class InstrumentAnalysis(models.Model):
    """
    Model used to track instrument statistics for a particular range.
    """

    '''
    Metadata
    '''
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_instrument_analyses'
        verbose_name = _('Instrument Analysis')
        verbose_name_plural = _('Instrument Analyses')
        unique_together = ("instrument", "start_dt", "finish_dt")
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


    '''
    Object Managers
    '''
    objects = InstrumentAnalysisManager()

    '''
    Fields
    '''

    #
    # Primary identification fields.
    #

    instrument = models.ForeignKey(
        "Instrument",
        help_text=_('The instrument that this anlysis will based on.'),
        blank=False,
        null=False,
        related_name="analyses",
        on_delete=models.CASCADE
    )
    start_dt = models.DateTimeField(
        _("Start Datetime"),
        help_text=_('The start date and time to base this analysis on.'),
        blank=False,
        null=False,
    )
    finish_dt = models.DateTimeField(
        _("Finish Datetime"),
        help_text=_('The end date and time to base this analysis on.'),
        blank=False,
        null=False,
    )

    #
    # Analysis fields.
    #

    min_value = models.FloatField(
        _("Minimum value"),
        help_text=_('The lowest possible value.'),
        blank=False,
        null=True,
    )
    min_timestamp = models.DateTimeField(
        _("Timestamp of minimum value"),
        help_text=_('The date and time that this minimum value occured on.'),
        blank=False,
        null=False,
    )
    max_value = models.FloatField(
        _("Maximum value"),
        help_text=_('The largest possible value.'),
        blank=False,
        null=True,
    )
    max_timestamp = models.DateTimeField(
        _("Timestamp of maximum value"),
        help_text=_('The date and time that this maximum value occured on.'),
        blank=False,
        null=False,
    )
    mean_value = models.FloatField(
        _("Mean value"),
        help_text=_('The mean value.'),
        blank=False,
        null=True,
    )
    median_value = models.FloatField(
        _("Median value"),
        help_text=_('The median value.'),
        blank=False,
        null=True,
    )
    mode_value = models.FloatField(
        _("Mode value"),
        help_text=_('The mode value.'),
        blank=False,
        null=True,
    )
    mode_values = JSONField(
        _("Mode values"),
        help_text=_('The mode values.'),
        blank=False,
        null=True,
    )
    range_value = models.FloatField(
        _("Range value"),
        help_text=_('The range value.'),
        blank=False,
        null=True,
    )
    stedv_value = models.FloatField(
        _("Standard deviation value"),
        help_text=_('The standard deviation value.'),
        blank=False,
        null=True,
    )
    variance_value = models.FloatField(
        _("Variance value"),
        help_text=_('The variance value.'),
        blank=False,
        null=True,
    )

    #
    # Reference fields.
    #

    report = models.ForeignKey(
        "DeviceReport",
        help_text=_('The device report that this analysis belongs to if it was generated for a particular report.'),
        blank=True,
        null=True,
        related_name="analyses",
        on_delete=models.SET_NULL
    )

    #
    # System fields.
    #

    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
