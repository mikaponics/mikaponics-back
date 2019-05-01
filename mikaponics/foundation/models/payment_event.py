# -*- coding: utf-8 -*-
import uuid
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import BrinIndex
from django.db import models
from django.utils.translation import ugettext_lazy as _


class PaymentEventLogManager(models.Manager):
    def delete_all(self):
        items = PaymentEventLog.objects.all()
        for item in items.all():
            item.delete()


class PaymentEvent(models.Model):
    """
    The model used to store the webhook data from Stripe.

    Model was built on Stripe API endpoint version "2019-02-19".
    """
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_payment_events'
        verbose_name = _('Payment Event')
        verbose_name_plural = _('Payment Events')
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
                fields=['created_at'],
                autosummarize=True,
            ),
        )

    objects = PaymentEventLogManager()

    '''
    Fields
    '''

    id = models.BigAutoField(
        _("ID"),
        primary_key=True,
    )


    #
    # Stripe webhook pre-pocessed data.
    #

    created = models.DateTimeField(
        _("Created"),
        help_text=_('The datetime this event was created by Stripe.'),
        blank=False,
        null=False,
    )
    livemode = models.BooleanField(
        _("livemode"),
        help_text=_('Track whether this event was from production environment or testing environment.'),
        blank=False,
        null=False,
    )
    event_id = models.CharField(
        _("Event ID"),
        max_length=127,
        help_text=_('The primary key used by Stripe.'),
        blank=False,
        null=False,
        db_index=True,
    )
    type = models.CharField(
        _("Type"),
        max_length=127,
        help_text=_('The type of event this is.'),
        blank=False,
        null=False,
        db_index=True,
    )
    object = models.CharField(
        _("Object"),
        max_length=63,
        help_text=_('The type of object this is.'),
        blank=False,
        null=False,
    )
    request = JSONField(
        _("Request"),
        help_text=_('The request data.'),
        blank=True,
        null=True,
    )
    pending_webhooks = models.PositiveSmallIntegerField(
        _("Pending Webhooks"),
        help_text=_('Is this from a pending webhook.'),
        blank=False,
        null=False,
    )
    api_version = models.CharField(
        _("API Version"),
        max_length=31,
        help_text=_('The API version used when this event was saved.'),
        blank=False,
        null=False,
    )
    data = JSONField(
        _("Raw Data"),
        help_text=_('The data that was sent by Stripe with this event.'),
        blank=False,
        null=False,
    )

    #
    # Post-processed data.
    #

    user = models.ForeignKey(
        "foundation.User",
        help_text=_('The user that this Stripe event is related to.'),
        blank=True,
        null=True,
        related_name="stripe_events",
        on_delete=models.CASCADE
    )
    invoice = models.ForeignKey(
        "Invoice",
        help_text=_('The invoices that this Stripe event is related to.'),
        blank=True,
        null=True,
        related_name="stripe_events",
        on_delete=models.CASCADE
    )

    #
    # Audit detail fields
    #

    created_at = models.DateTimeField(auto_now_add=True)
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
    # Note: Why are we not tracking last modified from IP, etc. The reason is
    #       because this model will only be processed by our applications
    #       backend.

    def __str__(self):
        return str(self.id)
