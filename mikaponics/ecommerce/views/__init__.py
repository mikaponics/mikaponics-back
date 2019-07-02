from ecommerce.views.resources.invoice_item_views import (
    InvoiceItemRetrieveUpdateDestroyAPIView
)
from ecommerce.views.resources.invoice_views import (
    InvoiceListCreateAPIView,
    InvoiceRetrieveDestroyAPIView,
    InvoiceRetrieveUpdateBillingAddressAPIView,
    InvoiceRetrieveUpdateShippingAddressAPIView,
    InvoiceSendEmailAPIView
)
from ecommerce.views.resources.onboarding_crud_views import OnboardingAPIView
from ecommerce.views.resources.purchase_device_crud_views import PurchaseDeviceAPIView
from ecommerce.views.resources.stripe_event_views import PaymentEventAPIView
from ecommerce.views.gui.email_views import (
    receipt_email_page,
    onboarded_email_page
)
from ecommerce.views.resources.purchase_subscription_crud_views import PurchaseSubscriptionAPIView
