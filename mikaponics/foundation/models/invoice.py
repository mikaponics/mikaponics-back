# -*- coding: utf-8 -*-
import uuid
from decimal import Decimal
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from djmoney.models.fields import MoneyField


class InvoiceManager(models.Manager):
    def delete_all(self):
        items = Invoice.objects.all()
        for item in items.all():
            item.delete()


class Invoice(models.Model):
    """
    The purchase invoice a user made with Mikaponics.
    """

    '''
    Metadata
    '''
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_invoices'
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')
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
    class ORDER_STATE:
        ERROR = 0
        DRAFT = 1
        PURCHASE_PENDING = 2
        PURCHASE_FAILED = 3
        PURCHASE_SUCCEEDED = 4
        BUILDING = 5
        SHIPPING = 6
        DELIVERED = 7

    ORDER_STATE_CHOICES = (
        (ORDER_STATE.DRAFT, _('Draft')),
        (ORDER_STATE.PURCHASE_PENDING, _('Purchase Pending')),
        (ORDER_STATE.PURCHASE_FAILED, _('Purchase Failed')),
        (ORDER_STATE.PURCHASE_SUCCEEDED, _('Purchased')),
        (ORDER_STATE.BUILDING, _('Building')),
        (ORDER_STATE.SHIPPING, _('Shipping / On route')),
        (ORDER_STATE.DELIVERED, _('Delivered')),
        (ORDER_STATE.ERROR, _('Error')),
    )

    '''
    Object Managers
    '''
    objects = InvoiceManager()

    '''
    Fields
    '''
    store = models.ForeignKey(
        "Store",
        help_text=_('The store this invoice belongs to.'),
        blank=False,
        null=False,
        related_name="invoices",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        "foundation.User",
        help_text=_('The user whom this purchase invoice belongs to.'),
        blank=False,
        null=False,
        related_name="invoices",
        on_delete=models.CASCADE
    )
    shipper = models.ForeignKey(
        "Shipper",
        help_text=_('The shipper whom is responsible for delivering this invoice.'),
        blank=True,
        null=True,
        related_name="invoices",
        on_delete=models.SET_NULL
    )
    state = models.PositiveSmallIntegerField(
        _("State"),
        help_text=_('The state of the invoice.'),
        blank=False,
        null=False,
        default=ORDER_STATE.DRAFT,
        choices=ORDER_STATE_CHOICES,
        editable=False, # Only device or web-app can change this state, not admin user!
    )

    #
    # Stripe Fields
    #

    stripe_receipt_id = models.CharField(
        _("Stripe Receipt ID"),
        help_text=_('The ID returned from <a href="https://stripe.com">stripe</a> for the charge transaction.'),
        blank=True,
        null=True,
        max_length=127,
    )
    stripe_receipt_data = JSONField(
        _("Stripe Receipt Data"),
        help_text=_('The receipt json data returned from <a href="https://stripe.com">stripe</a> for the charge transaction.'),
        blank=True,
        null=True,
        max_length=127,
    )

    #
    # Auto-calculated Fields
    #

    total_before_tax = MoneyField(
        _("Total (before tax)"),
        help_text=_('The total amount that must be paid for this invoice. Tax not included.'),
        max_digits=14,
        decimal_places=2,
        default_currency='CAD'
    )
    tax = MoneyField(
        _("Tax"),
        help_text=_('The tax that must be applied to this invoice.'),
        max_digits=14,
        decimal_places=2,
        default_currency='CAD'
    )
    total_after_tax = MoneyField(
        _("Total (after tax)"),
        help_text=_('The total amount that must be paid for this invoice. Tax included.'),
        max_digits=14,
        decimal_places=2,
        default_currency='CAD'
    )
    shipping = MoneyField(
        _("Shipping"),
        help_text=_('The shipping amount that must be paid to deliver this invoice.'),
        max_digits=14,
        decimal_places=2,
        default_currency='CAD'
    )
    credit = MoneyField(
        _("Credit"),
        help_text=_('The credit amount associated with this invoice.'),
        max_digits=14,
        decimal_places=2,
        default_currency='CAD'
    )
    grand_total = MoneyField(
        _("Grand Total"),
        help_text=_('The grand total after tax, shipping and discounts were applied.'),
        max_digits=14,
        decimal_places=2,
        default_currency='CAD'
    )

    #
    # Billing Address Fields
    #

    billing_given_name = models.CharField(
        _("Billing Given Name"),
        max_length=127,
        help_text=_('The first name used for billing.'),
    )
    billing_last_name = models.CharField(
        _("Billing Last Name"),
        max_length=127,
        help_text=_('The last name used for billing.'),
    )
    billing_email = models.EmailField(
        _("Billing Email"),
        max_length=127,
        help_text=_('The email used for billing'),
    )
    billing_telephone = models.CharField(
        _("Billing Telephone"),
        help_text=_('The telephone number used for billing.'),
        blank=True,
        null=True,
        max_length=31,
    )
    billing_country = models.CharField(
        _("Billing Country"),
        max_length=127,
        help_text=_('The country. For example, USA. You can also provide the two-letter <a href="https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements">ISO 3166-1 alpha-2</a> country code.'),
    )
    billing_locality = models.CharField(
        _("Billing Locality"),
        max_length=127,
        help_text=_('The locality. For example, Mountain View.'),
    )
    billing_region = models.CharField(
        _("Billing Region"),
        max_length=127,
        help_text=_('The region. For example, CA.'),
    )
    billing_post_office_box_number = models.CharField(
        _("Billing Post Office Box Number"),
        max_length=255,
        help_text=_('Apartment, suite, unit, building, floor, etc.'),
        blank=True,
        null=True,
    )
    billing_postal_code = models.CharField(
        _("Billing Postal Code"),
        max_length=127,
        help_text=_('The postal code. For example, 94043.'),
        db_index=True,
        blank=True,
        null=True,
    )
    billing_street_address = models.CharField(
        _("Billing Street Address"),
        max_length=255,
        help_text=_('The street address. For example, 1600 Amphitheatre Pkwy.'),
    )
    billing_street_address_extra = models.CharField(
        _("Billing Street Address (Extra Line)"),
        max_length=255,
        help_text=_('Apartment, suite, unit, building, floor, etc.'),
        blank=True,
        null=True,
    )

    #
    # Shipping Address Fields
    #

    shipping_given_name = models.CharField(
        _("Shipping Given Name"),
        max_length=127,
        help_text=_('The first name used for shipping'),
    )
    shipping_last_name = models.CharField(
        _("Shipping Last Name"),
        max_length=127,
        help_text=_('The last name used for shipping'),
    )
    shipping_email = models.EmailField(
        _("Shipping Email"),
        max_length=127,
        help_text=_('The email used for shipping.'),
    )
    shipping_telephone = models.CharField(
        _("Shipping Telephone"),
        help_text=_('The number used for shipper.'),
        blank=True,
        null=True,
        max_length=31,
    )
    shipping_country = models.CharField(
        _("Shipping Country"),
        max_length=127,
        help_text=_('The country. For example, USA. You can also provide the two-letter <a href="https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements">ISO 3166-1 alpha-2</a> country code.'),
    )
    shipping_locality = models.CharField(
        _("Shipping Locaility"),
        max_length=127,
        help_text=_('The locality. For example, Mountain View.'),
    )
    shipping_region = models.CharField(
        _("Shipping Region"),
        max_length=127,
        help_text=_('The region. For example, CA.'),
    )
    shipping_post_office_box_number = models.CharField(
        _("Shipping Post Office Box Number"),
        max_length=127,
        help_text=_('Apartment, suite, unit, building, floor, etc.'),
        blank=True,
        null=True,
    )
    shipping_postal_code = models.CharField(
        _("Shipping Postal Code"),
        max_length=127,
        help_text=_('The postal code. For example, 94043.'),
        db_index=True,
        blank=True,
        null=True,
    )
    shipping_street_address = models.CharField(
        _("Shipping Street Address"),
        max_length=255,
        help_text=_('The street address. For example, 1600 Amphitheatre Pkwy.'),
    )
    shipping_street_address_extra = models.CharField(
        _("Shipping Street Address (Extra Line)"),
        max_length=255,
        help_text=_('Apartment, suite, unit, building, floor, etc.'),
        blank=True,
        null=True,
    )

    #
    # Audit detail fields
    #

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        "foundation.User",
        help_text=_('The user whom created this purchase invoice.'),
        related_name="created_invoices",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        editable=False,
    )
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
    last_modified_by = models.ForeignKey(
        "foundation.User",
        help_text=_('The user whom last modified this purchase invoice.'),
        related_name="last_modified_invoices",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        editable=False,
    )
    last_modified_from = models.GenericIPAddressField(
        _("Last modified from IP"),
        help_text=_('The IP address of the modifier.'),
        blank=True,
        null=True,
        editable=False,
    )
    last_modified_from_is_public = models.BooleanField(
        _("Is Last modified from IP public?"),
        help_text=_('Is modifier a public IP and is routable.'),
        default=False,
        blank=True,
        editable=False,
    )

    '''
    Methods.
    '''

    def __str__(self):
        return str(self.id)

    @cached_property
    def total(self):
        """
        Function will calculate the invoice totals and return the calculation
        in JSON format.
        """
        # Calculate the total.
        self.total_before_tax.amount = 0
        for item in self.invoice_items.all():
            self.total_before_tax += (item.product_price * item.number_of_products)

        # Calculate the tax.
        from djmoney.money import Money

        tax_percent = self.store.get_tax_rate(self.shipping_country, self.shipping_region)
        if tax_percent:
            tax_rate = tax_percent / Decimal(100.00)
            tax = self.total_before_tax.amount * tax_rate
            self.tax = Money(amount=tax, currency=self.store.currency)
        self.total_after_tax = self.total_before_tax + self.tax

        # Calculate grand total
        self.grand_total = self.total_after_tax

        # Step 1: Apply the credit.
        if self.credit:
            self.grand_total -= self.credit

        # Step 2: Apply the shipping.
        if self.shipper:
            self.shipping = self.shipper.shipping_price
            self.grand_total += self.shipper.shipping_price

        # Save our model.
        self.save()

        # Return a summary of our computations.
        return {
            'total_before_tax': self.total_before_tax.amount,
            'tax': self.tax.amount,
            'total_after_tax': self.total_after_tax.amount,
            'shipping': self.shipping.amount,
            'credit': self.credit.amount,
            'grand_total': self.grand_total.amount,
            'grand_total_in_cents': self.grand_total.amount * 100
        }

    def invalidate(self, method_name):
        """
        Function used to clear the cache for the cached property functions.
        """
        try:
            if method_name == 'total':
                del self.total
            else:
                raise Exception("Method name not found.")
        except AttributeError:
            pass

    def get_grand_total_in_pennies(self):
        value = self.grand_total * Decimal(100.00)
        return int(value.amount)

    @cached_property
    def pretty_state(self):
        return dict(self.ORDER_STATE_CHOICES).get(self.state)