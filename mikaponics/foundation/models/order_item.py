# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField


class OrderItemManager(models.Manager):
    def delete_all(self):
        items = OrderItem.objects.all()
        for item in items.all():
            item.delete()


class OrderItem(models.Model):
    """
    The purchase order a user made with Mikaponics.
    """
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_order_items'
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
        default_permissions = ()
        permissions = (
            # ("can_get_opening_hours_specifications", "Can get opening hours specifications"),
            # ("can_get_opening_hours_specification", "Can get opening hours specifications"),
            # ("can_post_opening_hours_specification", "Can create opening hours specifications"),
            # ("can_put_opening_hours_specification", "Can update opening hours specifications"),
            # ("can_delete_opening_hours_specification", "Can delete opening hours specifications"),
        )

    objects = OrderItemManager()
    order = models.ForeignKey(
        "Order",
        help_text=_('The user whom this purchase order belongs to.'),
        blank=False,
        null=False,
        related_name="order_items",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        "Product",
        help_text=_('The product that will be ordered for this order item.'),
        blank=False,
        null=False,
        related_name="order_items",
        on_delete=models.CASCADE
    )
    number_of_products = models.PositiveSmallIntegerField(
        _("Number of products"),
        help_text=_('The number of `Products` this order item holds.'),
        default=1,
        blank=True,
        db_index=False,
    )
    product_price = MoneyField(
        _("Price of"),
        help_text=_('The price of a single `Product` for this order item.'),
        max_digits=14,
        decimal_places=2,
        default_currency='CAD'
    )

    def __str__(self):
        return str(self.id)
