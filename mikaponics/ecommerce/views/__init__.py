from ecommerce.views.resources.invoice_item_views import (
    InvoiceItemRetrieveUpdateDestroyAPIView
)
from ecommerce.views.resources.invoice_views import (
    InvoiceListCreateAPIView,
    InvoiceRetrieveDestroyAPIView,
    InvoiceRetrieveUpdateBillingAddressAPIView,
    InvoiceRetrieveUpdateShippingAddressAPIView
)
from ecommerce.views.resources.onboarding_crud_views import OnboardingAPIView
from ecommerce.views.resources.purchase_validator_func_views import PurchaseValidatorFuncAPIView;
from ecommerce.views.resources.invoice_func_views import InvoiceCalculationFuncView
from ecommerce.views.resources.stripe_event_views import PaymentEventAPIView
from ecommerce.views.gui.email_views import receipt_email_page
