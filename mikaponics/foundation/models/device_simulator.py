# -*- coding: utf-8 -*-
import pytz
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import BrinIndex
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _


class DeviceSimulatorManager(models.Manager):
    def delete_all(self):
        items = DeviceSimulator.objects.all()
        for item in items.all():
            item.delete()


class DeviceSimulator(models.Model):
    """
    Model used simulate the device data creation.
    """

    '''
    Metadata
    '''
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_device_simulators'
        verbose_name = _('Device Simulator')
        verbose_name_plural = _('Device Simulators')
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


    '''
    Object Managers
    '''
    objects = DeviceSimulatorManager()

    '''
    Fields
    '''

    #
    # Generic fields.
    #

    id = models.BigAutoField(
        _("ID"),
        primary_key=True,
    )
    device = models.OneToOneField(
        "Device",
        help_text=_('The device that this simulator will run for.'),
        blank=False,
        null=False,
        related_name="simulator",
        on_delete=models.CASCADE
    )
    is_running = models.BooleanField(
        _("Is Running"),
        help_text=_('Controls whether the simulator is running or not.'),
        default=True,
        blank=True,
    )

    #
    # System fields.
    #

    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    def tick(self):
        from foundation.models import Device, TimeSeriesDatum

        for instrument in self.device.instruments.all():

            # Make sure the device is active.
            instrument.device.state = Device.DEVICE_STATE.ONLINE
            instrument.device.save()

            TimeSeriesDatum.objects.seed(instrument, 1)

            # Reset the device's cached items.
            instrument.device.invalidate_all()
