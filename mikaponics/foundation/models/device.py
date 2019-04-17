# -*- coding: utf-8 -*-
import uuid
import pytz
from faker import Faker
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields import JSONField
from django.db import IntegrityError
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from oauthlib.common import generate_token
from oauth2_provider.models import (
    Application,
    AbstractApplication,
    AbstractAccessToken,
    AccessToken,
    RefreshToken
)

from foundation.constants import *


class DeviceManager(models.Manager):
    def delete_all(self):
        items = Device.objects.all()
        for item in items.all():
            item.delete()

    def seed(self, user, product, length=25):
        results = []
        faker = Faker('en_CA')
        for i in range(0,length):
            device = Device.objects.create(
                name = faker.domain_word(),
                description = faker.sentence(nb_words=6, variable_nb_words=True, ext_word_list=None),
                user = user,
                product = product,
            )
            results.append(device)
        return results


class Device(models.Model):
    """
    """

    '''
    Metadata
    '''
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_devices'
        verbose_name = _('Device')
        verbose_name_plural = _('Devices')
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
    class DEVICE_TYPE:
        LOGGER = 1

    DEVICE_TYPE_OF_CHOICES = (
        (DEVICE_TYPE.LOGGER, _('Data Logger')),
    )

    class DEVICE_STATE:
        NEW = 1
        ONLINE = 2
        OFFLINE = 3
        ERROR = 4

    DEVICE_STATE_CHOICES = (
        (DEVICE_STATE.NEW, _('New')),
        (DEVICE_STATE.ONLINE, _('Online')),
        (DEVICE_STATE.OFFLINE, _('Offline')),
        (DEVICE_STATE.ERROR, _('Error')),
    )

    '''
    Object Managers
    '''
    objects = DeviceManager()

    '''
    Fields
    '''

    #
    # Specific device fields.
    #

    uuid = models.UUIDField(
        help_text=_('The unique identifier used by us to identify a device in our system and we release this value to the customer.'),
        default=uuid.uuid4,
        null=False,
        editable=False,
        db_index=True,
        unique=True,
    )
    user = models.ForeignKey(
        "User",
        help_text=_('The user whom owns this device.'),
        blank=True,
        null=True,
        related_name="devices",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        "Product",
        help_text=_('The type of product this device is.'),
        blank=False,
        null=False,
        related_name="devices",
        on_delete=models.CASCADE
    )
    data_interval_in_seconds = models.PositiveSmallIntegerField(
        _("Data Interval (Seconds)"),
        help_text=_('The data interval all the instruments will poll by. Interval measured in seconds.'),
        blank=False,
        null=False,
        default=60, # 60 seconds is 1 minute.
    )
    activated_at = models.DateTimeField(
        _("Activated At"),
        help_text=_('The datetime that this device first made an API call to our API web-service.'),
        blank=True,
        null=True,
        editable=False,
    )
    timezone = models.CharField(
        _("Timezone"),
        help_text=_('The timezone of the device.'),
        max_length=32,
        choices=TIMEZONE_CHOICES,
        default="UTC"
    )
    invoice = models.ForeignKey(
        "Invoice",
        help_text=_('The e-commerce invoice this device is related to.'),
        blank=True,
        null=True,
        related_name="devices",
        on_delete=models.SET_NULL
    )
    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique slug used for this device when accessing device details page.'),
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
        help_text=_('The state of device.'),
        blank=False,
        null=False,
        default=DEVICE_STATE.NEW,
        choices=DEVICE_STATE_CHOICES,
        editable=False, # Only device or web-app can change this state, not admin user!
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
    last_measured_unit_of_measure = models.CharField(
        _("Last measured unit of measure"),
        help_text=_('The last measured unit of measure since operation.'),
        max_length=7,
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
        help_text=_('The manufacturer\'s name whom built the hardware that this device runs on. Ex: "Raspberry Pi Foundation".'),
        blank=True,
        default="",
        null=True,
    )
    hardware_product_name = models.CharField(
        _("Hardware Product Name"),
        max_length=31,
        help_text=_('The offical product name given by the manufacturer of the hardware that this device runs on. Ex: "Raspberry Pi 3 Model B+".'),
        blank=True,
        default="",
        null=True,
    )
    hardware_produt_id = models.CharField(
        _("Hardware Product ID"),
        max_length=31,
        help_text=_('The manufacturer\'s product ID of the hardware that this device runs on. Ex: "PI3P".'),
        blank=True,
        default="",
        null=True,
    )
    hardware_product_serial = models.CharField(
        _("Hardware Product Serial"),
        max_length=31,
        help_text=_('The serial number of the hardware that this device runs on. Ex: "0000000000000000".'),
        blank=True,
        default="",
    )

    #
    # https://schema.org/GeoCoordinates #
    #

    elevation = models.FloatField(
        _("Elevation"),
        help_text=_('The elevation of a location (<a href="https://en.wikipedia.org/wiki/World_Geodetic_System">WGS 84</a>).'),
        blank=True,
        null=True
    )
    location = PointField( # Combine latitude and longitude into a single field.
        _("Location"),
        help_text=_('A longitude and latitude coordinates of this device. For example -81.245277,42.984924 (<a href="https://en.wikipedia.org/wiki/World_Geodetic_System">WGS 84</a>).'),
        null=True,
        blank=True,
        srid=4326,
        db_index=True
    )

    #--------------------------#
    # https://schema.org/Place #
    #--------------------------#

    global_location_number = models.CharField(
        _("Global Location Number"),
        max_length=255,
        help_text=_('The <a href="https://www.gs1.org/standards/id-keys/gln">Global Location Number</a> (GLN, sometimes also referred to as International Location Number or ILN) of the respective organization, person, or place. The GLN is a 13-digit number used to identify parties and physical locations.'),
        blank=True,
        null=True,
    )

    #--------------------------#
    # https://schema.org/Thing #
    #--------------------------#

    name = models.CharField(
        _("Name"),
        max_length=255,
        help_text=_('The name of the name.'),
        blank=False,
        null=False,
    )
    alternate_name = models.CharField(
        _("Alternate Name"),
        max_length=255,
        help_text=_('An alias for the name.'),
        blank=True,
        null=True,
    )
    description = models.TextField(
        _("Description"),
        help_text=_('A description of the place.'),
        blank=True,
        null=True,
        default='',
    )
    url = models.URLField(
        _("URL"),
        help_text=_('URL of the device.'),
        null=True,
        blank=True
    )
    image = models.ImageField(
        upload_to = 'devices/',
        help_text=_('An image of the device.'),
        null=True,
        blank=True
    )
    identifier = models.CharField(
        _("Identifier"),
        max_length=255,
        help_text=_('The identifier property represents any kind of identifier for any kind of <a href="https://schema.org/Thing">Thing</a>, such as ISBNs, GTIN codes, UUIDs etc. Schema.org provides dedicated properties for representing many of these, either as textual strings or as URL (URI) links. See <a href="https://schema.org/docs/datamodel.html#identifierBg">background notes</a> for more details.'),
        blank=True,
        null=True,
    )

    #
    # Audit details
    #

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        "User",
        help_text=_('The user whom created this device.'),
        related_name="created_devices",
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
        help_text=_('The user whom last modified this device.'),
        related_name="last_modified_devices",
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

    def save(self, *args, **kwargs):
        """
        Override the save function so we can add extra functionality.

        (1) If we created the object then we will generate a custom slug.
        (a) If user exists then generate slug based on user's name.
        (b) Else generate slug with random string.
        """
        if not self.slug:
            # CASE 1 OF 2: HAS USER.
            if self.user:
                count = Device.objects.filter(user=self.user).count()
                count += 1
                try:
                    self.slug = slugify(self.user)+"-device-"+str(count)
                except IntegrityError as e:
                    if 'unique constraint' in e.message:
                        self.slug = slugify(self.user)+"-device-"+str(count)+"-"+get_random_string(length=5)
            # CASE 2 OF 2: DOES NOT HAVE USER.
            else:
                self.slug = "device-"+get_random_string(length=32)

        super(Device, self).save(*args, **kwargs)

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return "/device/"+str(self.slug)

    def get_environment_variables_file_url(self):
        aURL = None
        if self.id:
            aURL =  settings.MIKAPONICS_BACKEND_HTTP_PROTOCOL
            aURL += settings.MIKAPONICS_BACKEND_HTTP_DOMAIN
            aURL += reverse('mikaponics_device_environment_variable_file_detail', args=[self.id])
        return aURL

    def get_pretty_state(self):
        result = dict(self.DEVICE_STATE_CHOICES).get(self.state)
        return str(result)

    def get_pretty_last_measured_value(self):
        if self.last_measured_value:
            return str(self.last_measured_value)+" "+self.last_measured_unit_of_measure
        return _("No data available")

    def get_pretty_last_measured_at(self):
        if self.last_measured_at:
            return str(self.last_measured_at)
        return _("No data available")

    def invalidate(self, method_name):
        """
        Function used to clear the cache for the cached property functions.
        """
        try:
            if method_name == 'humidity_instrument':
                del self.humidity_instrument
            elif method_name == 'temperature_instrument':
                del self.temperature_instrument
            else:
                raise Exception("Method name not found.")
        except AttributeError:
            pass

    @cached_property
    def humidity_instrument(self):
        if self.instruments:
            from foundation.models.instrument import Instrument
            return self.instruments.filter(type_of=Instrument.INSTRUMENT_TYPE.HUMIDITY).first()
        return None

    @cached_property
    def temperature_instrument(self):
        if self.instruments:
            from foundation.models.instrument import Instrument
            return self.instruments.filter(type_of=Instrument.INSTRUMENT_TYPE.TEMPERATURE).first()
        return None

    def set_last_recorded_datum(self, datum):
        # Update our value.
        self.last_measured_value = datum.value
        self.last_measured_at = datum.timestamp
        self.last_measured_unit_of_measure = datum.get_unit_of_measure()
        self.save()

        # Clear our cache of previously saved values.
        self.invalidate('humidity_instrument')
        self.invalidate('temperature_instrument')
