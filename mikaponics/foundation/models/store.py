# -*- coding: utf-8 -*-
import uuid
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from djmoney.models.fields import MoneyField
from djmoney.forms.widgets import CURRENCY_CHOICES

from ecommerce.utils import get_country_code, get_country_province_code


def validate_tax_rate(value):
    if value >= 1 or value < -1:
        raise ValidationError(
            _('The value `%(value)s` is not a valid tax rate. Please pick between 0.99 to 0'),
            params={'value': value},
        )


class StoreManager(models.Manager):

    @cached_property
    def default_store(self):
        return Store.objects.all().first()

    def delete_all(self):
        items = Store.objects.all()
        for item in items.all():
            item.delete()


class Store(models.Model):
    """
    Model to represent a single store and the business details (ex: tax rate)
    associate with it.
    """
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_stores'
        verbose_name = _('Store')
        verbose_name_plural = _('Stores')
        default_permissions = ()
        permissions = (
            # ("can_get_opening_hours_specifications", "Can get opening hours specifications"),
            # ("can_get_opening_hours_specification", "Can get opening hours specifications"),
            # ("can_post_opening_hours_specification", "Can create opening hours specifications"),
            # ("can_put_opening_hours_specification", "Can update opening hours specifications"),
            # ("can_delete_opening_hours_specification", "Can delete opening hours specifications"),
        )

    objects = StoreManager()
    name = models.CharField(
        _("Name"),
        max_length=31,
        help_text=_('The official name of this store.'),
        blank=False,
        null=False,
    )
    currency = models.CharField(
        _("Currency"),
        max_length=3,
        help_text=_('The currency used by this store formatted in <a href="https://en.wikipedia.org/wiki/ISO_4217">ISO 4217</a> formatting.'),
        default="CAD",
        blank=True,
        null=False,
        choices=CURRENCY_CHOICES
    )
    timezone_name = models.CharField(
        _("Timezone Name"),
        max_length=63,
        help_text=_('The timezone for this store.'),
        default="America/Toronto",
        blank=True,
        null=False
    )
    tax_rates = JSONField(
        _("Tax"),
        help_text=_('The dictionary of tax rates to be looked up and applied on our e-commerce purchases.'),
        blank=True,
        null=False,
    )
    referrer_credit = MoneyField(
        _("Referrer Credit"),
        help_text=_('The credit amount that will be granted to device purchases for users whom referred new users to our store.'),
        max_digits=14,
        decimal_places=2,
        default_currency='CAD',
        blank=True,
        null=True,
    )
    referee_credit = MoneyField(
        _("Referee Credit"),
        help_text=_('The credit amount that will be granted to device purchases for users whom where referred to our store by existing users.'),
        max_digits=14,
        decimal_places=2,
        default_currency='CAD',
        blank=True,
        null=True,
    )

    def __str__(self):
        return str(self.name)

    def get_tax_rate(self, country_name, province_name):
        country_code = get_country_code(country_name)
        province_code = get_country_province_code(country_name, province_name)
        try:
            return Decimal(self.tax_rates[country_code][province_code])
        except KeyError:
            return None
