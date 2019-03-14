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
        app_label = 'ecommerce'
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
        "ecommerce.Store",
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
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='CAD')

    def __str__(self):
        return str(self.name)
