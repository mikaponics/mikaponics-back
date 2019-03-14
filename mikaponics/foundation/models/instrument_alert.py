# -*- coding: utf-8 -*-
import pytz
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class InstrumentAlertManager(models.Manager):
    def delete_all(self):
        items = InstrumentAlert.objects.all()
        for item in items.all():
            item.delete()

    def get_latest_by_device(self, device):
        try:
            return InstrumentAlert.objects.filter(datum__instrument__device=device).latest('created_at')
        except InstrumentAlert.DoesNotExist:
            return None

    def get_latest_by_instrument(self, instrument):
        try:
            return InstrumentAlert.objects.filter(instrument=instrument).latest('created_at')
        except InstrumentAlert.DoesNotExist:
            return None


class InstrumentAlert(models.Model):
    """
    """

    '''
    Metadata
    '''
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_instrument_alerts'
        verbose_name = _('Instrument Alert')
        verbose_name_plural = _('Instrument Alerts')
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

    class INSTRUMENT_ALERT_STATE:
        RED_ABOVE_VALUE = 1
        ORANGE_ABOVE_VALUE = 2
        YELLOW_ABOVE_VALUE = 3
        YELLOW_BELOW_VALUE = 4
        ORANGE_BELOW_VALUE = 5
        RED_BELOW_VALUE = 6


    INSTRUMENT_ALERT_STATE_CHOICES = (
        (INSTRUMENT_ALERT_STATE.RED_ABOVE_VALUE, _('Red (above value)')),
        (INSTRUMENT_ALERT_STATE.ORANGE_ABOVE_VALUE, _('Orange (above value)')),
        (INSTRUMENT_ALERT_STATE.YELLOW_ABOVE_VALUE, _('Yellow (above value)')),
        (INSTRUMENT_ALERT_STATE.YELLOW_BELOW_VALUE, _('Yellow (below value)')),
        (INSTRUMENT_ALERT_STATE.ORANGE_BELOW_VALUE, _('Orange (below value)')),
        (INSTRUMENT_ALERT_STATE.RED_BELOW_VALUE, _('Red (below value)')),
    )


    '''
    Object Managers
    '''
    objects = InstrumentAlertManager()

    '''
    Fields
    '''
    instrument = models.ForeignKey(
        "Instrument",
        help_text=_('The instrument this alert belongs to.'),
        blank=False,
        null=False,
        related_name="alerts",
        on_delete=models.CASCADE
    )
    datum_timestamp = models.DateTimeField(
        _("Datum Timestamp"),
        help_text=_('The date and time this datum was recorded at.'),
        blank=False,
        null=False,
    )
    datum_value = models.FloatField(
        _("Datum Value"),
        help_text=_('The value of the datum.'),
        blank=False,
        null=True,
    )
    state = models.PositiveSmallIntegerField(
        _("State"),
        help_text=_('The state of alert.'),
        blank=False,
        null=False,
        choices=INSTRUMENT_ALERT_STATE_CHOICES,
    )
    created_at = models.DateTimeField(
        _("Created at"),
        help_text=_('The data and time this alert was created.'),
        auto_now_add=True,
        db_index=True
    )

    '''
    Methods
    '''

    def __str__(self):
        return str(self.id)

    def get_pretty_state(self):
        return dict(self.INSTRUMENT_ALERT_STATE_CHOICES).get(self.state)

    def is_red_alert(self):
        return self.state == self.INSTRUMENT_ALERT_STATE.RED_ABOVE_VALUE or self.state == self.INSTRUMENT_ALERT_STATE.RED_BELOW_VALUE

    def is_orange_alert(self):
        return self.state == self.INSTRUMENT_ALERT_STATE.ORANGE_ABOVE_VALUE or self.state == self.INSTRUMENT_ALERT_STATE.ORANGE_BELOW_VALUE

    def is_yellow_alert(self):
        return self.state == self.INSTRUMENT_ALERT_STATE.YELLOW_ABOVE_VALUE or self.state == self.INSTRUMENT_ALERT_STATE.YELLOW_BELOW_VALUE
