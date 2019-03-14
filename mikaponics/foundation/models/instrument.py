# -*- coding: utf-8 -*-
import uuid
import pytz
from datetime import date, datetime, timedelta
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class InstrumentManager(models.Manager):
    def delete_all(self):
        items = Instrument.objects.all()
        for item in items.all():
            item.delete()


class Instrument(models.Model):
    """
    """

    '''
    Metadata
    '''
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_instruments'
        verbose_name = _('Instrument')
        verbose_name_plural = _('Instruments')
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
    class INSTRUMENT_TYPE:
        HUMIDITY = 1
        TEMPERATURE = 2

    INSTRUMENT_TYPE_OF_CHOICES = (
        (INSTRUMENT_TYPE.HUMIDITY, _('Humidity')),
        (INSTRUMENT_TYPE.TEMPERATURE, _('Temperature')),
    )

    class INSTRUMENT_STATE:
        NEW = 1
        CONNECTED = 2
        DISCONNECTED = 3
        ERROR = 4

    INSTRUMENT_STATE_CHOICES = (
        (INSTRUMENT_STATE.NEW, _('New')),
        (INSTRUMENT_STATE.CONNECTED, _('Connected')),
        (INSTRUMENT_STATE.DISCONNECTED, _('Disconnected')),
        (INSTRUMENT_STATE.ERROR, _('Error')),
    )

    class INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS:
        EVERY_MINUTE = 60
        EVERY_2_MINUTES = 120
        EVERY_5_MINUTES = 300
        EVERY_10_MINUTES = 600
        EVERY_20_MINUTES = 1200
        EVERY_30_MINUTES = 1800
        EVERY_HOUR = 3600
        EVERY_2_HOURS = 7200
        EVERY_4_HOURS = 14400
        EVERY_6_HOURS = 21600
        EVERY_12_HOURS = 43200
        EVERY_24_HOURS = 86400

    INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS_CHOICES = (
        (INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS.EVERY_MINUTE, _('Every minute')),
        (INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS.EVERY_2_MINUTES, _('Every 2 minutes')),
        (INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS.EVERY_5_MINUTES, _('Every 5 minutes')),
        (INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS.EVERY_10_MINUTES, _('Every 10 minutes')),
        (INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS.EVERY_20_MINUTES, _('Every 20 minutes')),
        (INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS.EVERY_30_MINUTES, _('Every 30 minutes')),
        (INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS.EVERY_HOUR, _('Every hour')),
        (INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS.EVERY_2_HOURS, _('Every 2 hours')),
        (INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS.EVERY_4_HOURS, _('Every 4 hours')),
        (INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS.EVERY_6_HOURS, _('Every 6 hours')),
        (INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS.EVERY_12_HOURS, _('Every 12 hours')),
        (INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS.EVERY_24_HOURS, _('Every 24 hours')),
    )

    '''
    Object Managers
    '''
    objects = InstrumentManager()

    '''
    Fields
    '''
    uuid = models.UUIDField(
        help_text=_('The unique identifier used by us to identify an instrument in our system and we release this value to the customer.'),
        default=uuid.uuid4,
        null=False,
        editable=False,
        db_index=True,
        unique=True,
    )
    device = models.ForeignKey(
        "Device",
        help_text=_('The device which this instrument belongs to.'),
        blank=True,
        null=True,
        related_name="instruments",
        on_delete=models.CASCADE
    )
    type_of = models.PositiveSmallIntegerField(
        _("type of"),
        help_text=_('The type of instrument this is.'),
        blank=False,
        null=False,
        choices=INSTRUMENT_TYPE_OF_CHOICES,
    )
    configuration = JSONField(
        _("Configuration"),
        help_text=_('The configuration details of this instrument with device.'),
        blank=False,
        null=False,
    )

    #
    # Real-time operation fields.
    #

    state = models.PositiveSmallIntegerField(
        _("State"),
        help_text=_('The state of instrument.'),
        blank=False,
        null=False,
        default=INSTRUMENT_STATE.NEW,
        choices=INSTRUMENT_STATE_CHOICES,
        editable=False, # Note: Only instrument or web-app can change this state, not admin user!
    )
    last_recorded_datum = models.ForeignKey(
        "TimeSeriesDatum",
        help_text=_('The last record datum for this instrument.'),
        blank=True,
        null=True,
        related_name="+", # Note: Uni-directional relationship.
        on_delete=models.SET_NULL,
        editable=False, # Note: Only instrument or web-app can change this value, not admin user!
    )
    statistics = JSONField(
        _("Statistics"),
        help_text=_('The current operational statistics for this instrument.'),
        blank=True,
        null=True,
        editable=False, # Note: Only instrument or web-app can change this value, not admin user!
    )

    #
    # Hardware Product Information
    #
    hardware_manufacturer = models.CharField(
        _("Hardware Manufacturer"),
        max_length=31,
        help_text=_('The manufacturer\'s name whom built the hardware that this instrument runs on. Ex: "Phidgets Inc.".'),
        blank=True,
        default="",
        null=True,
    )
    hardware_product_name = models.CharField(
        _("Hardware Product Name"),
        max_length=31,
        help_text=_('The offical product name given by the manufacturer of the hardware instrument. Ex: "Humidity Phidget".'),
        blank=True,
        default="",
        null=True,
    )
    hardware_produt_id = models.CharField(
        _("Hardware Product ID"),
        max_length=31,
        help_text=_('The product ID of the hardware that this instrument runs on. Ex: "HUM1000_0".'),
        blank=True,
        default="",
        null=True,
    )
    hardware_product_serial = models.CharField(
        _("Hardware Product Serial"),
        max_length=31,
        help_text=_('The serial number of the hardware that this instrument runs on. Ex: "000000".'),
        blank=True,
        default="",
    )

    #
    # Alarm configuration.
    #

    max_value = models.FloatField(
        _("Max value"),
        help_text=_('The maximum value supported by the instrument. Anything larger then this value is impossible by this instrument. Please see this instrument\'s manual for this value.'),
        blank=True,
        null=True,
    )
    red_above_value = models.FloatField(
        _("Red above value"),
        help_text=_('The value that if is greater then or equal to then our system will trigger a red alert.'),
        blank=True,
        null=True,
    )
    orange_above_value = models.FloatField(
        _("Orange above value"),
        help_text=_('The value that if is greater then or equal to then our system will orange a yellow alert.'),
        blank=True,
        null=True,
    )
    yellow_above_value = models.FloatField(
        _("Yellow above value"),
        help_text=_('The value that if is greater then or equal to then our system will trigger a yellow alert.'),
        blank=True,
        null=True,
    )
    yellow_below_value = models.FloatField(
        _("Yellow below value"),
        help_text=_('The value that if is less then or equal to then our system will trigger a yellow alert.'),
        blank=True,
        null=True,
    )
    orange_below_value = models.FloatField(
        _("Orange below value"),
        help_text=_('The value that if is less then or equal to then our system will trigger a orange alert.'),
        blank=True,
        null=True,
    )
    red_below_value = models.FloatField(
        _("Red below value"),
        help_text=_('The value that if is less then or equal to then our system will trigger a red alert.'),
        blank=True,
        null=True,
    )
    min_value = models.FloatField(
        _("Min value"),
        help_text=_('The minimum value supported by the instrument. Anything smaller then this value is impossible by this instrument. Please see this instrument\'s manual for this value.'),
        blank=True,
        null=True,
    )
    red_alert_delay_in_seconds = models.PositiveSmallIntegerField(
        _("Red alert delay (seconds)"),
        help_text=_('The time that red alerts will be sent from the last time the red alert was sent.'),
        blank=True,
        null=False,
        default=INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS.EVERY_MINUTE,
        choices=INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS_CHOICES,
    )
    orange_alert_delay_in_seconds = models.PositiveSmallIntegerField(
        _("Orange alert delay (seconds)"),
        help_text=_('The time that orange alerts will be sent from the last time the orange alert was sent.'),
        blank=True,
        null=False,
        default=INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS.EVERY_MINUTE,
        choices=INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS_CHOICES,
    )
    yellow_alert_delay_in_seconds = models.PositiveSmallIntegerField(
        _("Yellow alert delay (seconds)"),
        help_text=_('The time that yellow alerts will be sent from the last time the yellow alert was sent.'),
        blank=True,
        null=False,
        default=INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS.EVERY_MINUTE,
        choices=INSTRUMENT_ALERT_FREQUENCY_IN_SECONDS_CHOICES,
    )

    #
    # Audit details
    #

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        "User",
        help_text=_('The user whom created this instrument.'),
        related_name="created_instruments",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        editable=False,
    )
    created_from = models.GenericIPAddressField(
        _("Created from IP"),
        help_text=_('The IP address of the creator.'),
        blank=True,
        null=True,
        editable=False,
    )
    created_from_is_public = models.BooleanField(
        _("Is created from IP public?"),
        help_text=_('Is creator a public IP and is routable.'),
        default=False,
        blank=True,
        editable=False,
    )
    last_modified_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        "User",
        help_text=_('The user whom last modified this instrument.'),
        related_name="last_modified_instruments",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        editable=False,
    )
    last_modified_from = models.GenericIPAddressField(
        _("Last modified from IP"),
        help_text=_('The IP address of the modifier.'),
        blank=True,
        null=True,
        editable=False,
    )
    last_modified_from_is_public = models.BooleanField(
        _("Is Last modified from IP public?"),
        help_text=_('Is modifier a public IP and is routable.'),
        default=False,
        blank=True,
        editable=False,
    )

    '''
    Class methods.
    '''

    def __str__(self):
        return "#"+str(self.id)+" - "+str(self.get_pretty_instrument_type_of())

    def get_pretty_instrument_type_of(self):
        return dict(self.INSTRUMENT_TYPE_OF_CHOICES).get(self.type_of)

    def get_absolute_url(self):
        return reverse('mikaponics_instrument_detail', args=[self.id])

    def get_unit_of_measure(self):
        if self.type_of == Instrument.INSTRUMENT_TYPE.HUMIDITY:
            return "%"
        elif self.type_of == Instrument.INSTRUMENT_TYPE.TEMPERATURE:
            return "℃"
        return ""

    def get_icon(self):
        """
        Returns the `fontawesome` icon for this instrument.
        """
        if self.type_of == Instrument.INSTRUMENT_TYPE.HUMIDITY:
            return "tint"
        elif self.type_of == Instrument.INSTRUMENT_TYPE.TEMPERATURE:
            return "thermometer-three-quarters"
        return ""

    def invalidate(self, method_name):
        """
        Function used to clear the cache for the cached property functions.
        """
        try:
            if method_name == 'last_measured_value':
                del self.last_measured_value
            elif method_name == 'last_measured_timestamp':
                del self.last_measured_timestamp
            elif method_name == 'pretty_last_measured_value':
                del self.pretty_last_measured_value
            elif method_name == 'pretty_last_measured_timestamp':
                del self.pretty_last_measured_timestamp
            else:
                raise Exception("Method name not found.")
        except AttributeError:
            pass

    def get_pretty_instrument_type_of(self):
        return dict(self.INSTRUMENT_TYPE_OF_CHOICES).get(self.type_of)

    @cached_property
    def last_measured_value(self):
        if self.last_recorded_datum:
            return self.last_recorded_datum.value
        return None

    @cached_property
    def last_measured_timestamp(self):
        if self.last_recorded_datum:
            naive_dt = self.last_recorded_datum.timestamp
            utc_aware_dt = naive_dt.replace(tzinfo=pytz.utc)
            return utc_aware_dt
        return None

    @cached_property
    def pretty_last_measured_value(self):
        if self.last_recorded_datum:
            return self.last_recorded_datum.get_pretty_value()
        return None

    @cached_property
    def pretty_last_measured_timestamp(self):
        if self.last_recorded_datum:
            return self.last_recorded_datum.get_pretty_timestamp()
        return None

    def set_last_recorded_datum(self, datum):
        # Update our value.
        self.last_recorded_datum = datum
        self.save()

        # Clear our cache of previously saved values.
        self.invalidate('last_measured_value')
        self.invalidate('last_measured_timestamp')
        self.invalidate('pretty_last_measured_value')
        self.invalidate('pretty_last_measured_timestamp')

    def get_alert_state_by_datum(self, datum):
        """
        Function used to check if the time-series datum would trigger an alert
        and return the alert status of the datum in the parameter. Returns the
        status by the parameter datum.
        """
        from foundation.models.instrument_alert import InstrumentAlert
        if datum.value:
            if self.red_above_value:
                if datum.value >= self.red_above_value:
                    return InstrumentAlert.INSTRUMENT_ALERT_STATE.RED_ABOVE_VALUE
            if self.orange_above_value:
                if datum.value >= self.orange_above_value:
                    return InstrumentAlert.INSTRUMENT_ALERT_STATE.ORANGE_ABOVE_VALUE
            if self.yellow_above_value:
                if datum.value >= self.yellow_above_value:
                    return InstrumentAlert.INSTRUMENT_ALERT_STATE.YELLOW_ABOVE_VALUE
            if self.red_below_value:
                if datum.value <= self.red_below_value:
                    return InstrumentAlert.INSTRUMENT_ALERT_STATE.RED_BELOW_VALUE
            if self.orange_below_value:
                if datum.value <= self.orange_below_value:
                    return InstrumentAlert.INSTRUMENT_ALERT_STATE.ORANGE_BELOW_VALUE
            if self.yellow_below_value:
                if datum.value <= self.yellow_below_value:
                    return InstrumentAlert.INSTRUMENT_ALERT_STATE.YELLOW_BELOW_VALUE
        return None

    def find_alarming_datum(self, start_dt, end_dt, skip_datum=None):
        """
        Function will look through all the time-series data from the start
        datetime to the end datetime range to find the LATEST datum which will
        trigger an alarm. The priority of states would be:
        - Red above value
        - Orange above value
        - Yellow above value
        - Red below value
        - Orange below value
        - Yellow below value
        """
        data = self.time_series_data.filter(
            Q(timestamp__range=[start_dt, end_dt])&
            ~Q(id=skip_datum.id)
        ).order_by('-id').iterator(chunk_size=250)

        for datum in data:
            alert_state = self.get_possible_alert_state_by_datum(datum)
            if alert_state:
                return dateum, alert_state
        return None, None
