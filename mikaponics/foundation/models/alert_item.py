# -*- coding: utf-8 -*-
import pytz
from django.contrib.auth import get_user_model
from django.contrib.postgres.indexes import BrinIndex
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class AlertItemManager(models.Manager):
    def delete_all(self):
        items = AlertItem.objects.all()
        for item in items.all():
            item.delete()


class AlertItem(models.Model):
    """
    Class used as the unified alert item used in our system.
    """

    '''
    Metadata
    '''
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_alarm_items'
        verbose_name = _('Alert Item')
        verbose_name_plural = _('Alert Items')
        default_permissions = ()
        permissions = ()
        indexes = (
            BrinIndex(
                fields=['created_at'],
                autosummarize=True,
            ),
        )
        index_together = (
            ('user', 'type_of', 'state', 'created_at', ),
        )

    '''
    Constants & Choices
    '''

    class ALERT_TYPE_OF:
        PRODUCTION = 1
        PRODUCTION_CROP = 2
        DEVICE = 3
        INSTRUMENT = 4

    ALERT_TYPE_OF_CHOICES = (
        (ALERT_TYPE_OF.PRODUCTION, _('Production')),
        (ALERT_TYPE_OF.PRODUCTION_CROP, _('Production Crop')),
        (ALERT_TYPE_OF.DEVICE, _('Device')),
        (ALERT_TYPE_OF.INSTRUMENT, _('Instrument')),
    )

    class ALERT_ITEM_STATE:
        ACTIVE = 1
        ARCHIVED = 2

    ALERT_ITEM_STATE_CHOICES = (
        (ALERT_ITEM_STATE.ACTIVE, _('Active')),
        (ALERT_ITEM_STATE.ARCHIVED, _('Archived')),
    )

    class ALERT_ITEM_CONDITION:
        RED_ABOVE_VALUE = 1
        ORANGE_ABOVE_VALUE = 2
        YELLOW_ABOVE_VALUE = 3
        YELLOW_BELOW_VALUE = 4
        ORANGE_BELOW_VALUE = 5
        RED_BELOW_VALUE = 6


    ALERT_ITEM_CONDITION_CHOICES = (
        (ALERT_ITEM_CONDITION.RED_ABOVE_VALUE, _('Red (above value)')),
        (ALERT_ITEM_CONDITION.ORANGE_ABOVE_VALUE, _('Orange (above value)')),
        (ALERT_ITEM_CONDITION.YELLOW_ABOVE_VALUE, _('Yellow (above value)')),
        (ALERT_ITEM_CONDITION.YELLOW_BELOW_VALUE, _('Yellow (below value)')),
        (ALERT_ITEM_CONDITION.ORANGE_BELOW_VALUE, _('Orange (below value)')),
        (ALERT_ITEM_CONDITION.RED_BELOW_VALUE, _('Red (below value)')),
    )


    '''
    Object Managers
    '''
    objects = AlertItemManager()

    '''
    Fields
    '''
    id = models.BigAutoField(
        _("ID"),
        primary_key=True,
    )
    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique slug used for this alert item when accessing details page.'),
        max_length=255,
        blank=False,
        null=False,
        db_index=True,
        unique=True,
        editable=False, # Only device or web-app can change this state, not admin user!
    )
    user = models.ForeignKey(
        "User",
        help_text=_('The user this alert belongs to.'),
        blank=False,
        null=False,
        related_name="alerts",
        on_delete=models.CASCADE
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of alert.'),
        blank=False,
        null=False,
        choices=ALERT_TYPE_OF_CHOICES,
    )
    device = models.ForeignKey(
        "Device",
        help_text=_('The device this alert belongs to.'),
        blank=True,
        null=True,
        related_name="alerts",
        on_delete=models.SET_NULL
    )
    instrument = models.ForeignKey(
        "Instrument",
        help_text=_('The instrument this alert belongs to.'),
        blank=True,
        null=True,
        related_name="alerts",
        on_delete=models.SET_NULL
    )
    production = models.ForeignKey(
        "Production",
        help_text=_('The production this alert belongs to.'),
        blank=True,
        null=True,
        related_name="alerts",
        on_delete=models.SET_NULL
    )
    production_crop = models.ForeignKey(
        "ProductionCrop",
        help_text=_('The production crop this alert belongs to.'),
        blank=True,
        null=True,
        related_name="alerts",
        on_delete=models.SET_NULL
    )
    timestamp = models.DateTimeField(
        _("Timestamp"),
        help_text=_('The date and time recorded to to cause this alert.'),
        blank=False,
        null=False,
    )
    value = models.FloatField(
        _("Value"),
        help_text=_('The value that caused this alert.'),
        blank=False,
        null=True,
    )
    state = models.PositiveSmallIntegerField(
        _("State"),
        help_text=_('The state of alert.'),
        blank=False,
        null=False,
        choices=ALERT_ITEM_STATE_CHOICES,
    )
    condition = models.PositiveSmallIntegerField(
        _("Condition"),
        help_text=_('The condition of alert.'),
        blank=False,
        null=False,
        choices=ALERT_ITEM_CONDITION_CHOICES,
    )
    created_at = models.DateTimeField(
        _("Created at"),
        help_text=_('The data and time this alert was created.'),
        auto_now_add=True,
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
            count = AlertItem.objects.filter(user=self.user).count()
            count += 1

            # Generate our slug.
            self.slug = slugify(self.user)+"-alert-"+str(count)

            # If a unique slug was not found then we will keep searching
            # through the various slugs until a unique slug is found.
            while AlertItem.objects.filter(slug=self.slug).exists():
                self.slug = slugify(self.user)+"-alert-"+str(count)+"-"+get_random_string(length=8)

        super(AlertItem, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.slug)

    def get_absolute_url(self):
        if self.type_of == self.ALERT_TYPE_OF.INSTRUMENT:
            return "/instrument-alert/"+str(self.slug)
        return "/alert/"+str(self.slug)

    def get_pretty_type_of(self):
        result = dict(self.ALERT_TYPE_OF_CHOICES).get(self.type_of)
        return str(result)

    def get_pretty_state(self):
        result = dict(self.ALERT_TYPE_OF_CHOICES).get(self.state)
        return str(result)

    def get_pretty_condition(self):
        return dict(self.ALERT_ITEM_CONDITION_CHOICES).get(self.condition)

    def is_red_alert(self):
        return self.condition == self.ALERT_ITEM_CONDITION.RED_ABOVE_VALUE or self.condition == self.ALERT_ITEM_CONDITION.RED_BELOW_VALUE

    def is_orange_alert(self):
        return self.condition == self.ALERT_ITEM_CONDITION.ORANGE_ABOVE_VALUE or self.condition == self.ALERT_ITEM_CONDITION.ORANGE_BELOW_VALUE

    def is_yellow_alert(self):
        return self.condition == self.ALERT_ITEM_CONDITION.YELLOW_ABOVE_VALUE or self.condition == self.ALERT_ITEM_CONDITION.YELLOW_BELOW_VALUE

    def get_icon(self):
        if self.is_red_alert():
            return "fire"
        elif self.is_orange_alert():
            return "exclamation-circle"
        elif self.is_yellow_alert():
            return "exclamation-triangle"
        return None
