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

    '''
    Constants & Choices
    '''

    class STATE:
        DRAFT = 1
        COMING_SOON = 2
        PUBLISHED = 3
        HIDDEN = 4

    STATE_CHOICES = (
        (STATE.DRAFT, _('Draft')),
        (STATE.COMING_SOON, _('Coming Soon')),
        (STATE.HIDDEN, _('Hidden')),
        (STATE.PUBLISHED, _('Publised')),
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
    state = models.PositiveSmallIntegerField(
        _("State"),
        help_text=_('The state of product.'),
        blank=False,
        null=False,
        default=STATE.DRAFT,
        choices=STATE_CHOICES,
    )
    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique slug used for this product.'),
        max_length=127,
        blank=False,
        null=False,
        db_index=True,
        unique=True,
    )
    sort_number = models.PositiveSmallIntegerField(
        _("Sort #"),
        help_text=_('The sort number of product.'),
        blank=False,
        null=False,
        default=0,
    )
    icon = models.CharField(
        _("Icon"),
        max_length=31,
        help_text=_('The icon for this product.'),
        blank=False,
        null=False,
    )
    name = models.CharField(
        _("Name"),
        max_length=31,
        help_text=_('The name of this product.'),
        blank=False,
        null=False,
    )
    short_description = models.CharField(
        _("Short Description"),
        max_length=127,
        help_text=_('The short description of this product.'),
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
