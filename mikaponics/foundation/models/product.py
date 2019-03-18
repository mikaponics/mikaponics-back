# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField


class ProductManager(models.Manager):
    def delete_all(self):
        items = Product.objects.all()
        for item in items.all():
            item.delete()


class Product(models.Model):
    """
    The product
    """
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_products'
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        default_permissions = ()
        permissions = (
            # ("can_get_opening_hours_specifications", "Can get opening hours specifications"),
            # ("can_get_opening_hours_specification", "Can get opening hours specifications"),
            # ("can_post_opening_hours_specification", "Can create opening hours specifications"),
            # ("can_put_opening_hours_specification", "Can update opening hours specifications"),
            # ("can_delete_opening_hours_specification", "Can delete opening hours specifications"),
        )

    objects = ProductManager()
    store = models.ForeignKey(
        "Store",
        help_text=_('The store this product belongs to.'),
        blank=False,
        null=False,
        related_name="products",
        on_delete=models.CASCADE
    )
    name = models.CharField(
        _("Name"),
        max_length=31,
        help_text=_('The name of this product.'),
        blank=False,
        null=False,
    )
    description = models.TextField(
        _("Description"),
        help_text=_('A description of the product.'),
        blank=True,
        null=True,
        default='',
    )
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='CAD')
    payment_product_id = models.CharField(
        _("Payment Product ID"),
        max_length=127,
        help_text=_('The product ID set by the payment merchant.'),
        blank=True,
        null=True,
    )

    def __str__(self):
        return str(self.name)
