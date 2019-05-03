# -*- coding: utf-8 -*-
from django.db import models
from django.utils import crypto
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField



def get_random_code():
    return crypto.get_random_string(
        length=31,
        allowed_chars='abcdefghijkmnpqrstuvwxyz'
                      'ABCDEFGHIJKLMNPQRSTUVWXYZ'
                      '23456789'
    )


class CouponManager(models.Manager):
    def delete_all(self):
        items = Coupon.objects.all()
        for item in items.all():
            item.delete()


class Coupon(models.Model):
    '''
    Metadata
    '''
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_coupons'
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')
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
    class COUPON_STATE:
        ACTIVE = 1
        EXPIRED = 2
        CONSUMED = 3
        DEACTIVATED = 4

    COUPON_STATE_CHOICES = (
        (COUPON_STATE.ACTIVE, _('Active')),
        (COUPON_STATE.EXPIRED, _('Expired')),
        (COUPON_STATE.CONSUMED, _('Consumed')),
        (COUPON_STATE.DEACTIVATED, _('Deactivated')),
    )

    '''
    Object Managers
    '''
    objects = CouponManager()

    '''
    Fields
    '''

    id = models.BigAutoField(
        _("ID"),
        primary_key=True,
    )
    state = models.PositiveSmallIntegerField(
        _("State"),
        help_text=_('The state of coupon.'),
        blank=False,
        null=False,
        default=COUPON_STATE.ACTIVE,
        choices=COUPON_STATE_CHOICES,
    )
    expires_at = models.DateTimeField(
        _("Expires At"),
        help_text=_('The datatime this coupon will expire. If nothing is set then this coupon will never expire.'),
        blank=True,
        null=True,
    )
    credit = MoneyField(
        _("Credit"),
        help_text=_('The credit amount that will be applied to the invoice one-time.'),
        max_digits=14,
        decimal_places=2,
        default_currency='CAD',
        blank=False,
        null=False,
    )
    belongs_to = models.ForeignKey(
        "foundation.User",
        help_text=_('The user whom can only access this coupon. If no user is set then this coupon is open to everyone who knows the coupon code.'),
        related_name="belonging_coupons",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    usage_limit = models.PositiveSmallIntegerField(
        _("Usage Limit"),
        help_text=_('The number of times this coupon can be used before it is no longer active. If no usage limit was set then this coupon can be used an unlimited number of times.'),
        blank=False,
        null=False,
        default=1
    )
    code = models.CharField(
        _("Code"),
        help_text=_('The coupon code which can be given out.'),
        max_length=31,
        blank=True,
        null=True,
        db_index=True,
        unique=True,
        default=get_random_code
    )

    #
    # Audit detail fields
    #

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "foundation.User",
        help_text=_('The user whom created this coupon.'),
        related_name="created_coupons",
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
        help_text=_('The user whom last modified this coupon.'),
        related_name="last_modified_coupons",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        editable=False,
    )
    last_modified_from = models.GenericIPAddressField(
        _("Last modified from IP"),
        help_text=_('The IP address of the coupon.'),
        blank=True,
        null=True,
        editable=False,
    )
    last_modified_from_is_public = models.BooleanField(
        _("Is Last modified from IP public?"),
        help_text=_('Is coupon a public IP and is routable.'),
        default=False,
        blank=True,
        editable=False,
    )

    def __str__(self):
        return str(self.id)

    def claim(self, invoice=None):
        if self.usage_limit == 1:
            self.state = self.COUPON_STATE.CONSUMED
        else:
            self.usage_limit = self.usage_limit - 1
        self.save()
