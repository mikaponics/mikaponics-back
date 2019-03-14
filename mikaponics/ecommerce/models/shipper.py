# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField


class ShipperManager(models.Manager):
    def delete_all(self):
        items = Shipper.objects.all()
        for item in items.all():
            item.delete()


class Shipper(models.Model):
    """
    The product
    """
    class Meta:
        app_label = 'ecommerce'
        db_table = 'mika_shippers'
        verbose_name = _('Shipper')
        verbose_name_plural = _('Shippers')
        default_permissions = ()
        permissions = (
            # ("can_get_opening_hours_specifications", "Can get opening hours specifications"),
            # ("can_get_opening_hours_specification", "Can get opening hours specifications"),
            # ("can_post_opening_hours_specification", "Can create opening hours specifications"),
            # ("can_put_opening_hours_specification", "Can update opening hours specifications"),
            # ("can_delete_opening_hours_specification", "Can delete opening hours specifications"),
        )

    objects = ShipperManager()
    store = models.ForeignKey(
        "ecommerce.Store",
        help_text=_('The store this shipper belongs to.'),
        blank=False,
        null=False,
        related_name="shippers",
        on_delete=models.CASCADE
    )
    name = models.CharField(
        _("Name"),
        max_length=31,
        help_text=_('The name of this shipper.'),
        blank=False,
        null=False,
    )
    shipping_price = MoneyField(
        _("Shipping Price"),
        help_text=_('The price of shipping.'),
        max_digits=14,
        decimal_places=2,
        default_currency='CAD'
    )

    def __str__(self):
        return str(self.id)
