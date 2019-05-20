# -*- coding: utf-8 -*-
import uuid
import pytz
from datetime import date, datetime, timedelta
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import BrinIndex
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.crypto import get_random_string
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
        indexes = (
            BrinIndex(
                fields=['created_at', 'last_modified_at'],
                autosummarize=True,
            ),
        )

    '''
    Constants & Choices
    '''
    class INSTRUMENT_TYPE:
        HUMIDITY = 1
        TEMPERATURE = 2
        TVOC = 3
        CO2 = 4
        AIR_PRESSURE = 5
        ALTITUDE = 6
        WATER_LEVEL = 7
        POWER_USAGE = 8
        PH = 9
        EC = 10
        ORP = 11
        CAMERA = 12
        HEAT_VISION = 13
        UV_LIGHT = 14
        TRIAD_SPECTROSCOPY = 15

    INSTRUMENT_TYPE_OF_CHOICES = (
        (INSTRUMENT_TYPE.HUMIDITY, _('Humidity')),
        (INSTRUMENT_TYPE.TEMPERATURE, _('Temperature')),
        (INSTRUMENT_TYPE.TVOC, _('Total Volatile Organic Compound')),
        (INSTRUMENT_TYPE.CO2, _('Carbon Dioxide')),
        (INSTRUMENT_TYPE.AIR_PRESSURE, _('Air Pressure')),
        (INSTRUMENT_TYPE.ALTITUDE, _('Altitude')),
        (INSTRUMENT_TYPE.WATER_LEVEL, _('Water Level')),
        (INSTRUMENT_TYPE.POWER_USAGE, _('Power Usage')),
        (INSTRUMENT_TYPE.PH, _('pH')),
        (INSTRUMENT_TYPE.EC, _('Electrical Conductivity')),
        (INSTRUMENT_TYPE.ORP, _('Oxidation-Reduction Potential')),
        (INSTRUMENT_TYPE.CAMERA, _('Camera')),
        (INSTRUMENT_TYPE.HEAT_VISION, _('Heat Vision')),
        (INSTRUMENT_TYPE.UV_LIGHT, _('UV Light')),
        (INSTRUMENT_TYPE.TRIAD_SPECTROSCOPY, _('Triad Spectroscopy')),
    )

    class INSTRUMENT_STATE:
        NEW = 1
        CONNECTED = 2
        DISCONNECTED = 3
        ERROR = 4
        ARCHIVED = 5 # A.k.a. "Deleted".

    INSTRUMENT_STATE_CHOICES = (
        (INSTRUMENT_STATE.NEW, _('New')),
        (INSTRUMENT_STATE.CONNECTED, _('Connected')),
        (INSTRUMENT_STATE.DISCONNECTED, _('Disconnected')),
        (INSTRUMENT_STATE.ERROR, _('Error')),
        (INSTRUMENT_STATE.ARCHIVED, _('Archived')),
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
    data_interval_in_seconds = models.PositiveSmallIntegerField(
        _("Data Interval (Seconds)"),
        help_text=_('The data interval this instrument will poll by. Interval measured in seconds.'),
        blank=True,
        null=False,
        default=60, # 60 seconds is 1 minute.
    )
    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique slug used for this instrument when accessing details page.'),
        max_length=127,
        blank=True,
        null=False,
        db_index=True,
        unique=True,
        editable=False,
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
    last_measured_value = models.FloatField(
        _("Last measured value"),
        help_text=_('The last measured value since operation.'),
        blank=True,
        null=True,
        editable=False,
    )
    last_measured_at = models.DateTimeField(
        _("Last measured at"),
        help_text=_('The datetime of the last measured value since operation.'),
        blank=True,
        null=True,
        editable=False,
    )
    last_24h_min_value = models.FloatField(
        _("Last 24h minimum value"),
        help_text=_('The lastest measured minimum value within the last 24 hours of operation.'),
        blank=True,
        null=True,
        editable=False,
    )
    last_24h_min_timestamp_at = models.DateTimeField(
        _("Last 24h minimum datetime"),
        help_text=_('The datetime of the last 24h measured minimum value since operation.'),
        blank=True,
        null=True,
        editable=False,
    )
    last_24h_max_value = models.FloatField(
        _("Last 24h maximum value"),
        help_text=_('The lastest measured maximum value within the last 24 hours of operation.'),
        blank=True,
        null=True,
        editable=False,
    )
    last_24h_max_timestamp_at = models.DateTimeField(
        _("Last 24h maximum datetime"),
        help_text=_('The datetime of the last 24h measured maximum value since operation.'),
        blank=True,
        null=True,
        editable=False,
    )
    last_24h_mean_value = models.FloatField(
        _("Last 24h mean value"),
        help_text=_('The latest measured mean value within the last 24 hours of operation.'),
        blank=True,
        null=True,
        editable=False,
    )
    last_24h_median_value = models.FloatField(
        _("Last 24h median value"),
        help_text=_('The latest measured median value within the last 24 hours of operation.'),
        blank=True,
        null=True,
        editable=False,
    )
    last_24h_mode_value = models.FloatField(
        _("Last 24h mode value"),
        help_text=_('The latest measured mode value within the last 24 hours of operation.'),
        blank=True,
        null=True,
        editable=False,
    )
    last_24h_mode_values = JSONField(
        _("last 24h mode values"),
        help_text=_('The latest measured mode values within the last 24 hours of operation.'),
        blank=True,
        null=True,
        editable=False,
    )
    last_24h_range_value = models.FloatField(
        _("Last 24h range value"),
        help_text=_('The latest measured range value within the last 24 hours of operation.'),
        blank=True,
        null=True,
        editable=False,
    )
    last_24h_stedv_value = models.FloatField(
        _("last_24h_stedv_value"),
        help_text=_('The standard deviation value of the past 24 hours.'),
        blank=True,
        null=True,
        editable=False,
    )
    last_24h_variance_value = models.FloatField(
        _("last_24h_variance_value"),
        help_text=_('The variance value of the past 24 hours.'),
        blank=True,
        null=True,
        editable=False,
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
    def save(self, *args, **kwargs):
        """
        Override the save function so we can add extra functionality.

        (1) If we created the object then we will generate a custom slug.
        (a) If user exists then generate slug based on user's name.
        (b) Else generate slug with random string.
        """
        if not self.slug:
            # CASE 1 OF 2: HAS USER.
            if self.device.user:
                count = Instrument.objects.filter(device=self.device).count()
                count += 1

                # Generate our slug.
                self.slug = self.device.slug+"-instrument-"+str(count)

                # If a unique slug was not found then we will keep searching
                # through the various slugs until a unique slug is found.
                while Instrument.objects.filter(slug=self.slug).exists():
                    self.slug = self.device.slug+"-instrument-"+str(count)+"-"+get_random_string(length=8)

            # CASE 2 OF 2: DOES NOT HAVE USER.
            else:
                self.slug = "instrument-"+get_random_string(length=32)

            # Attach the instrument type to the slug.
            self.slug = self.slug +"-"+slugify(self.get_pretty_instrument_type_of())
            self.slug = self.slug.lower()

        # Call the parent class and load the default the save functionality.
        super(Instrument, self).save(*args, **kwargs)

    def __str__(self):
        return self.slug

    def get_pretty_state(self):
        result = dict(self.INSTRUMENT_STATE_CHOICES).get(self.state)
        return str(result)

    def get_pretty_last_measured_value(self):
        if self.last_measured_value:
            return str(self.last_measured_value)+" "+self.get_unit_of_measure()
        return _("No data available")

    def get_pretty_last_measured_at(self):
        if self.last_measured_at:
            return str(self.last_measured_at)
        return _("No data available")

    def get_pretty_instrument_type_of(self):
        result = dict(self.INSTRUMENT_TYPE_OF_CHOICES).get(self.type_of)
        return str(result)

    def get_absolute_url(self):
        return "/instrument/"+str(self.slug)

    def get_absolute_parent_url(self):
        return self.device.get_absolute_url()

    def get_unit_of_measure(self):
        if self.type_of == Instrument.INSTRUMENT_TYPE.HUMIDITY:
            return "%"
        elif self.type_of == Instrument.INSTRUMENT_TYPE.TEMPERATURE:
            return "℃"
        elif self.type_of == Instrument.INSTRUMENT_TYPE.TVOC:
            return "PPB"
        elif self.type_of == Instrument.INSTRUMENT_TYPE.CO2:
            return "PPM"
        elif self.type_of == Instrument.INSTRUMENT_TYPE.AIR_PRESSURE:
            return "Pa"
        elif self.type_of == Instrument.INSTRUMENT_TYPE.ALTITUDE:
            return "ft"
        elif self.type_of == Instrument.INSTRUMENT_TYPE.WATER_LEVEL:
            return "m"
        elif self.type_of == Instrument.INSTRUMENT_TYPE.POWER_USAGE:
            return "kw/h"
        elif self.type_of == Instrument.INSTRUMENT_TYPE.PH:
            return ""
        elif self.type_of == Instrument.INSTRUMENT_TYPE.EC:
            return ""
        elif self.type_of == Instrument.INSTRUMENT_TYPE.ORP:
            return ""
        elif self.type_of == Instrument.INSTRUMENT_TYPE.CAMERA:
            return ""
        elif self.type_of == Instrument.INSTRUMENT_TYPE.HEAT_VISION:
            return ""
        elif self.type_of == Instrument.INSTRUMENT_TYPE.UV_LIGHT:
            return ""
        elif self.type_of == Instrument.INSTRUMENT_TYPE.TRIAD_SPECTROSCOPY:
            return ""
        return ""

    def get_icon(self):
        """
        Returns the `fontawesome` icon for this instrument.
        """
        if self.type_of == Instrument.INSTRUMENT_TYPE.HUMIDITY:
            return "tint"
        elif self.type_of == Instrument.INSTRUMENT_TYPE.TEMPERATURE:
            return "thermometer-three-quarters"

        elif self.type_of == Instrument.INSTRUMENT_TYPE.TVOC:
            return "wind"

        elif self.type_of == Instrument.INSTRUMENT_TYPE.CO2:
            return "wind"

        elif self.type_of == Instrument.INSTRUMENT_TYPE.AIR_PRESSURE:
            return "wind"

        elif self.type_of == Instrument.INSTRUMENT_TYPE.ALTITUDE:
            return "mountain"

        elif self.type_of == Instrument.INSTRUMENT_TYPE.WATER_LEVEL:
            return "water"

        elif self.type_of == Instrument.INSTRUMENT_TYPE.POWER_USAGE:
            return "plug"

        elif self.type_of == Instrument.INSTRUMENT_TYPE.PH:
            return "vial"

        elif self.type_of == Instrument.INSTRUMENT_TYPE.EC:
            return "vial"

        elif self.type_of == Instrument.INSTRUMENT_TYPE.ORP:
            return "vial"

        elif self.type_of == Instrument.INSTRUMENT_TYPE.CAMERA:
            return "camera"

        elif self.type_of == Instrument.INSTRUMENT_TYPE.HEAT_VISION:
            return "fire"

        elif self.type_of == Instrument.INSTRUMENT_TYPE.UV_LIGHT:
            return "sun"

        elif self.type_of == Instrument.INSTRUMENT_TYPE.TRIAD_SPECTROSCOPY:
            return "sun"

        return ""

    def get_pretty_instrument_type_of(self):
        result = dict(self.INSTRUMENT_TYPE_OF_CHOICES).get(self.type_of)
        return str(result)

    def set_last_recorded_datum(self, datum):
        # Update our value.
        self.last_measured_value = datum.value
        self.last_measured_at = datum.timestamp
        self.last_measured_unit_of_measure = datum.get_unit_of_measure()
        self.save()

    def get_alert_state_by_datum(self, datum):
        """
        Function used to check if the time-series datum would trigger an alert
        and return the alert status of the datum in the parameter. Returns the
        status by the parameter datum.
        """
        from foundation.models.alert_item import AlertItem
        if datum.value:
            if self.red_above_value:
                if datum.value >= self.red_above_value:
                    return AlertItem.INSTRUMENT_ALERT_STATE.RED_ABOVE_VALUE
            if self.orange_above_value:
                if datum.value >= self.orange_above_value:
                    return AlertItem.INSTRUMENT_ALERT_STATE.ORANGE_ABOVE_VALUE
            if self.yellow_above_value:
                if datum.value >= self.yellow_above_value:
                    return AlertItem.INSTRUMENT_ALERT_STATE.YELLOW_ABOVE_VALUE
            if self.red_below_value:
                if datum.value <= self.red_below_value:
                    return AlertItem.INSTRUMENT_ALERT_STATE.RED_BELOW_VALUE
            if self.orange_below_value:
                if datum.value <= self.orange_below_value:
                    return AlertItem.INSTRUMENT_ALERT_STATE.ORANGE_BELOW_VALUE
            if self.yellow_below_value:
                if datum.value <= self.yellow_below_value:
                    return AlertItem.INSTRUMENT_ALERT_STATE.YELLOW_BELOW_VALUE
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
