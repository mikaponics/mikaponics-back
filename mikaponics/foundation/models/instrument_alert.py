# -*- coding: utf-8 -*-
import pytz
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db import models
from django.template.defaultfilters import slugify
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
    id = models.BigAutoField(
        _("ID"),
        primary_key=True,
        auto_created=True,
    )
    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique slug used for this instrument alert when accessing details page.'),
        max_length=255,
        blank=False,
        null=False,
        db_index=True,
        unique=True,
        editable=False, # Only device or web-app can change this state, not admin user!
    )
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

    def save(self, *args, **kwargs):
        """
        Override the save function so we can add extra functionality.

        (1) If we created the object then we will generate a custom slug.
        (a) If user exists then generate slug based on user's name.
        (b) Else generate slug with random string.
        """
        if not self.slug:
            # CASE 1 OF 2: HAS USER.
            if self.instrument.device.user:
                count = InstrumentAlert.objects.filter(instrument__device__user=self.instrument.device.user).count()
                count += 1
                try:
                    self.slug = slugify(self.instrument.device.user)+"-instrument-alert-"+str(count)
                except IntegrityError as e:
                    if 'unique constraint' in e.message:
                        self.slug = slugify(self.user)+"-instrument-alert-"+str(count)+"-"+get_random_string(length=5)
            # CASE 2 OF 2: DOES NOT HAVE USER.
            else:
                self.slug = "instrument-alert-"+get_random_string(length=32)

        super(InstrumentAlert, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return "/instrument-alert/"+str(self.slug)

    def get_pretty_state(self):
        return dict(self.INSTRUMENT_ALERT_STATE_CHOICES).get(self.state)

    def is_red_alert(self):
        return self.state == self.INSTRUMENT_ALERT_STATE.RED_ABOVE_VALUE or self.state == self.INSTRUMENT_ALERT_STATE.RED_BELOW_VALUE

    def is_orange_alert(self):
        return self.state == self.INSTRUMENT_ALERT_STATE.ORANGE_ABOVE_VALUE or self.state == self.INSTRUMENT_ALERT_STATE.ORANGE_BELOW_VALUE

    def is_yellow_alert(self):
        return self.state == self.INSTRUMENT_ALERT_STATE.YELLOW_ABOVE_VALUE or self.state == self.INSTRUMENT_ALERT_STATE.YELLOW_BELOW_VALUE

    def get_icon(self):
        if self.is_red_alert():
            return "fire"
        elif self.is_orange_alert():
            return "exclamation-circle"
        elif self.is_yellow_alert():
            return "exclamation-triangle"
        return None
