# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField


class InvoiceItemManager(models.Manager):
    def delete_all(self):
        items = InvoiceItem.objects.all()
        for item in items.all():
            item.delete()


class InvoiceItem(models.Model):
    """
    The purchase invoice a user made with Mikaponics.
    """
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_invoice_items'
        verbose_name = _('Invoice Item')
        verbose_name_plural = _('Invoice Items')
        default_permissions = ()
        permissions = (
            # ("can_get_opening_hours_specifications", "Can get opening hours specifications"),
            # ("can_get_opening_hours_specification", "Can get opening hours specifications"),
            # ("can_post_opening_hours_specification", "Can create opening hours specifications"),
            # ("can_put_opening_hours_specification", "Can update opening hours specifications"),
            # ("can_delete_opening_hours_specification", "Can delete opening hours specifications"),
        )

    objects = InvoiceItemManager()
    id = models.BigAutoField(
        _("ID"),
        primary_key=True,
    )
    invoice = models.ForeignKey(
        "Invoice",
        help_text=_('The user whom this purchase invoice belongs to.'),
        blank=False,
        null=False,
        related_name="invoice_items",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        "Product",
        help_text=_('The product that will be invoiceed for this invoice item.'),
        blank=False,
        null=False,
        related_name="invoice_items",
        on_delete=models.CASCADE
    )
    description = models.CharField(
        _("Description"),
        max_length=127,
        help_text=_('The description of the invoice item.'),
        blank=False,
        null=False,
    )
    quantity = models.PositiveSmallIntegerField(
        _("Quantity"),
        help_text=_('The number of `Products` this invoice item holds.'),
        default=1,
        blank=True,
        db_index=False,
    )
    unit_price = MoneyField(
        _("Unit Price"),
        help_text=_('The price of a single `Product` for this invoice item.'),
        max_digits=14,
        decimal_places=2,
        default_currency='CAD'
    )
    total_price = MoneyField(
        _("Total Price"),
        help_text=_('The total price of all `Products` in this invoice item.'),
        max_digits=14,
        decimal_places=2,
        default_currency='CAD'
    )

    def __str__(self):
        return str(self.id)
