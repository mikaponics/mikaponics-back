from ecommerce.views.resources.product_list_views import (
    ProductListAPIView
)
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
from ecommerce.views.resources.stripe_event_views import PaymentEventAPIView
from ecommerce.views.gui.email_views import (
    receipt_email_page,
    onboarded_email_page
)
from ecommerce.views.resources.subscription_crud_views import SubscriptionAPIView
from ecommerce.views.resources.calculate_purchase_device_func_view import CalculatePurchaseDeviceFuncAPIView
from ecommerce.views.resources.purchase_crud_views import PurchaseAPIView
