# -*- coding: utf-8 -*-
import pytz
from datetime import datetime, timedelta
from faker import Faker
from django.contrib.auth import get_user_model
from django.contrib.gis.db.models import PointField
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


class TimeSeriesDatumManager(models.Manager):
    def delete_all(self):
        items = TimeSeriesDatum.objects.all()
        for item in items.all():
            item.delete()

    def seed(self, instrument, length=25):
        # Pre-generate our timestamps.
        dt_array = []
        for i in range(0,length):
            # Create our datetime.
            dt = timezone.now() - timedelta(minutes=i)
            dt = dt.replace(second=0, microsecond=0)
            dt_array.append(dt)

        # Create the `time_step` we will be using.
        time_step = timezone.now() - timedelta(minutes=i)
        time_step = time_step.replace(hour=0, minute=1, second=0, microsecond=0)

        # Generate our time-series data. We will iterate through our
        # timestamps array in reverse so the OLDEST records get created FIRST
        # until the NEWEST records are created LAST; therefore, our time-series
        # data will be in the natural invoice.
        results = []
        faker = Faker('en_CA')
        previous = None
        for dt in reversed(dt_array):
            # Create the current record.
            data, was_created = TimeSeriesDatum.objects.get_or_create(
                instrument = instrument,
                timestamp = dt,
                defaults = {
                    'instrument': instrument,
                    'timestamp': dt,
                    'value': faker.pyfloat(left_digits=2, right_digits=2, positive=True),
                    'time_step': time_step,
                    'previous':  previous,
                }
            )
            results.append(data)

            # Save the previous record to have this current record as new.
            if previous:
                previous.next = data
                previous.save()

            # This record becomes the previous record.
            previous = data
        return results


class TimeSeriesDatum(models.Model):
    """
    """

    '''
    Metadata
    '''
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_time_series_data'
        verbose_name = _('Time-Series Datum')
        verbose_name_plural = _('Time-Series Data')
        default_permissions = ()
        unique_together = ("instrument", "timestamp")
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
    objects = TimeSeriesDatumManager()

    '''
    Fields
    '''

    #
    # Essential time-series datum fields.
    #

    id = models.BigAutoField(
        _("ID"),
        primary_key=True,
    )
    instrument = models.ForeignKey(
        "Instrument",
        help_text=_('The instrument this datum belongs to.'),
        blank=False,
        null=False,
        related_name="time_series_data",
        on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(
        _("Timestamp"),
        help_text=_('The date and time this datum was recorded at.'),
        blank=False,
        null=False,
    )
    time_step = models.TimeField(
        _("Time Step"),
        help_text=_('The time difference between the previous time series datum to this time-series datum.'),
        blank=False,
        null=False,
    )
    value = models.FloatField(
        _("Value"),
        help_text=_('The value of the datum.'),
        blank=True,
        null=True,
    )
    location = PointField(
        _("Location"),
        help_text=_('A longitude and latitude coordinates of this time-series datum.'),
        null=True,
        blank=True,
        srid=4326,
        db_index=True
    )
    image = models.ImageField(
        _("Image"),
        help_text=_('The image file of the time-series datum.'),
        blank=True,
        null=True,
        upload_to='uploads/time-series-data/%Y/%m/%d/'
    )
    file = models.FileField(
        _("File"),
        help_text=_('The generic file of the time-series datum.'),
        blank=True,
        null=True,
        upload_to='uploads/time-series-data/%Y/%m/%d/'
    )

    #
    # Additional fields for enhancement.
    #

    # NOTE: We want to structure this model to support a chained linked-list
    # data structure so we can do aggregate date modifications more easily.
    previous = models.ForeignKey(
        "self",
        help_text=_('The previous time-series datum in the chain of successive invoices based on time.'),
        blank=True,
        null=True,
        related_name="+",
        on_delete=models.SET_NULL,
        editable=False, # Only device or web-app can change this state, not admin user!
    )
    next = models.ForeignKey(
        "self",
        help_text=_('The next time-series datum in the chain of successive invoices based on time.'),
        blank=True,
        null=True,
        related_name="+",
        on_delete=models.SET_NULL,
        editable=False, # Only device or web-app can change this state, not admin user!
    )

    def __str__(self):
        return str(self.id)

    def get_unit_of_measure(self):
        return self.instrument.get_unit_of_measure()

    def get_pretty_value(self):
        """
        Function will add the unit of measurement with the value
        """
        return str(self.value) + " " + self.instrument.get_unit_of_measure()

    def get_pretty_timestamp(self):
        # Make sure our value is UTC aware.
        utc_aware_dt = self.timestamp.replace(tzinfo=pytz.utc)

        # Convert to the instruments local timezone.
        local_timezone = pytz.timezone(self.instrument.device.timezone)
        local_aware_dt = utc_aware_dt.astimezone(local_timezone) # Convert to local timezone.

        # Convert to the "SHORT_DATETIME" format. Note: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        return local_aware_dt.strftime("%d/%m/%Y %-I:%M %p")

    def get_pretty_instrument(self):
        return self.instrument.get_pretty_instrument_type_of()

    # def get_def get_absolute_url(self):
    #     return reverse('mikaponics_device_detail', args=[self.id])n reverse('mikaponics_device_detail', args=[self.id])
