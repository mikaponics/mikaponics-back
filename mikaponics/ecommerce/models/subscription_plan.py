# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField


class SubscriptionPlanManager(models.Manager):
    def delete_all(self):
        items = SubscriptionPlan.objects.all()
        for item in items.all():
            item.delete()


class SubscriptionPlan(models.Model):
    """
    The product
    """

    '''
    Metadata
    '''
    class Meta:
        app_label = 'ecommerce'
        db_table = 'mika_subscription_plans'
        verbose_name = _('Subscription Plan')
        verbose_name_plural = _('Subscription Plans')
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
    class INTERVAL_STATE:
        MONTHLY = 1
        ANNUALLY = 2

    INTERVAL_STATE_CHOICES = (
        (INTERVAL_STATE.MONTHLY, _("Monthly")),
        (INTERVAL_STATE.ANNUALLY, _("Annually")),
    )

    '''
    Object Managers
    '''
    objects = SubscriptionPlanManager()

    '''
    Fields
    '''
    store = models.ForeignKey(
        "ecommerce.Store",
        help_text=_('The store this product belongs to.'),
        blank=False,
        null=False,
        related_name="subscriptions",
        on_delete=models.CASCADE
    )
    name = models.CharField(
        _("Name"),
        max_length=31,
        help_text=_('The name of this product.'),
        blank=False,
        null=False,
    )
    amount = MoneyField(
        _("Amount"),
        help_text=_('A positive integer in cents (or 0 for a free plan) representing how much to charge on a recurring basis.'),
        max_digits=14,
        decimal_places=2,
        default_currency='CAD'
    )
    interval = models.CharField(
        _("Interval"),
        max_length=31,
        help_text=_('The frequency with which a subscription should be billed.'),
        blank=False,
        null=False,
        choices=INTERVAL_STATE_CHOICES,
    )
    payment_product_id = models.CharField(
        _("Payment Product ID"),
        max_length=127,
        help_text=_('The product ID set by the payment merchant.'),
        blank=True,
        null=True,
    )
    payment_plan_id = models.CharField(
        _("Payment Plan ID"),
        max_length=127,
        help_text=_('The plan ID set by the payment merchant.'),
        blank=True,
        null=True,
    )

    '''
    Methods.
    '''

    def __str__(self):
        return str(self.name)
