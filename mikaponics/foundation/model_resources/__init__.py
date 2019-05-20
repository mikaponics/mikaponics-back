from foundation.model_resources.device_resources import get_device_configuration_data
from foundation.model_resources.alert_item_resources import (
    create_alert_item_in_system_if_possible,
    can_alert_create_alert_in_system,
    alert_find_alarming_datum_in_system
)
from foundation.model_resources.user_resources import get_staff_email_addresses
from foundation.model_resources.coupon_resources import (
    grant_referral_program_coupons,
    find_usable_coupon_for_user
)
