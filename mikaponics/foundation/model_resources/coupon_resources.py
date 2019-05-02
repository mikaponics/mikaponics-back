from foundation.models import User, Store
from foundation.models.coupon import Coupon


def grant_referral_program_coupons(referrer=None, referee=None):
    """
    Function used to generate two (one-time usage) coupons to the referee
    (the new user in the system) and the referrer (the user whom referred
    this newly registered user). The coupon discount credit is set by our
    `store` object.
    """
    default_store = Store.objects.default_store;
    if referrer:
        Coupon.objects.create(
            state=Coupon.COUPON_STATE.ACTIVE,
            expires_at=None,
            credit=default_store.referrer_credit,
            belongs_to=referrer,
            usage_limit=1
        )
        if referrer.latest_invoice:
            referrer.latest_invoice.invalidate('total')
            referrer.invalidate('draft_invoice')
            referrer.invalidate('latest_invoice')
    if referee:
        Coupon.objects.create(
            state=Coupon.COUPON_STATE.ACTIVE,
            expires_at=None,
            credit=default_store.referee_credit,
            belongs_to=referee,
            usage_limit=1
        )
        if referee.latest_invoice:
            referee.latest_invoice.invalidate('total')
            referee.invalidate('draft_invoice')
            referee.invalidate('latest_invoice')


def find_usable_coupon_for_user(user):
    """
    Returns the next available (earliest) coupon to use.
    """
    return Coupon.objects.filter(
       belongs_to=user,
       state=Coupon.COUPON_STATE.ACTIVE,
       usage_limit__gte=1
    ).order_by('id').first()
