from ecommerce.views.resources.order_item_views import (
    OrderItemRetrieveUpdateDestroyAPIView
)
from ecommerce.views.resources.order_views import (
    OrderRetrieveUpdateBillingAddressAPIView,
    OrderRetrieveUpdateShippingAddressAPIView
)
from ecommerce.views.resources.purchase_validator_func_views import (
    PurchaseValidatorFuncAPIView
)
from ecommerce.views.resources.order_func_views import OrderCalculationFuncView
from ecommerce.views.resources.stripe_event_views import StripeEventAPIView
from ecommerce.views.gui.email_views import receipt_email_page
