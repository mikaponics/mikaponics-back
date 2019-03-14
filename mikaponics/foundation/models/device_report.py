# -*- coding: utf-8 -*-
import pytz
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class DeviceReportManager(models.Manager):
    def delete_all(self):
        items = DeviceReport.objects.all()
        for item in items.all():
            item.delete()


class DeviceReport(models.Model):
    """
    The model used to store all our computations based on our device. These
    computations will contain analysis, aggregation and various computations
    that will make up a report that is consumable by the `user`.
    """

    '''
    Metadata
    '''
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_device_reports'
        verbose_name = _('Device Report')
        verbose_name_plural = _('Device Reports')
        unique_together = ("device", "label", "start_dt", "finish_dt")
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
    objects = DeviceReportManager()

    '''
    Fields
    '''
    device = models.ForeignKey(
        "Device",
        help_text=_('The device which this report is based on.'),
        blank=False,
        null=False,
        related_name="reports",
        on_delete=models.CASCADE
    )
    label = models.CharField(
        _("Label"),
        max_length=31,
        help_text=_('The text label to briefly describe this device report.'),
        blank=False,
        null=False,
    )
    start_dt = models.DateTimeField(
        _("Start Datetime"),
        help_text=_('The start date and time to base this report on.'),
        blank=False,
        null=False,
    )
    finish_dt = models.DateTimeField(
        _("Finish Datetime"),
        help_text=_('The end date and time to base this report on.'),
        blank=False,
        null=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
