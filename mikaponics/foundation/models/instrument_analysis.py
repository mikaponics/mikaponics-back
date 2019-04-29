# -*- coding: utf-8 -*-
import pytz
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.crypto import get_random_string
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

    id = models.BigAutoField(
        _("ID"),
        primary_key=True,
    )
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
    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique slug used for this instrument analysis when accessing details page.'),
        max_length=127,
        blank=False,
        null=False,
        db_index=True,
        unique=True,
        editable=False,
    )

    #
    # Analysis fields.
    #

    min_value = models.FloatField(
        _("Minimum value"),
        help_text=_('The lowest possible value.'),
        blank=True,
        null=True,
    )
    min_timestamp = models.DateTimeField(
        _("Timestamp of minimum value"),
        help_text=_('The date and time that this minimum value occured on.'),
        blank=True,
        null=False,
    )
    max_value = models.FloatField(
        _("Maximum value"),
        help_text=_('The largest possible value.'),
        blank=True,
        null=True,
    )
    max_timestamp = models.DateTimeField(
        _("Timestamp of maximum value"),
        help_text=_('The date and time that this maximum value occured on.'),
        blank=True,
        null=False,
    )
    mean_value = models.FloatField(
        _("Mean value"),
        help_text=_('The mean value.'),
        blank=True,
        null=True,
    )
    median_value = models.FloatField(
        _("Median value"),
        help_text=_('The median value.'),
        blank=True,
        null=True,
    )
    mode_value = models.FloatField(
        _("Mode value"),
        help_text=_('The mode value.'),
        blank=True,
        null=True,
    )
    mode_values = JSONField(
        _("Mode values"),
        help_text=_('The mode values.'),
        blank=True,
        null=True,
    )
    range_value = models.FloatField(
        _("Range value"),
        help_text=_('The range value.'),
        blank=True,
        null=True,
    )
    stedv_value = models.FloatField(
        _("Standard deviation value"),
        help_text=_('The standard deviation value.'),
        blank=True,
        null=True,
    )
    variance_value = models.FloatField(
        _("Variance value"),
        help_text=_('The variance value.'),
        blank=True,
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

    def save(self, *args, **kwargs):
        """
        Override the save function so we can add extra functionality.

        (1) If we created the object then we will generate a custom slug.
        (a) If user exists then generate slug based on user's name.
        (b) Else generate slug with random string.
        """
        if not self.slug:
            # CASE 1 OF 2: HAS USER.
            if self.instrument:
                count = InstrumentAnalysis.objects.filter(instrument=self.instrument).count()
                count += 1

                # Generate our slug.
                self.slug = slugify(self.instrument)+"-analysis-"+str(count)

                # If a unique slug was not found then we will keep searching
                # through the various slugs until a unique slug is found.
                while InstrumentAnalysis.objects.filter(slug=self.slug).exists():
                    self.slug = slugify(self.instrument)+"-analysis-"+str(count)+"-"+get_random_string(length=8)

            # CASE 2 OF 2: DOES NOT HAVE USER.
            else:
                self.slug = "-analysis-"+get_random_string(length=32)

        super(InstrumentAnalysis, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return "/instrument/analysis/"+str(self.slug)
