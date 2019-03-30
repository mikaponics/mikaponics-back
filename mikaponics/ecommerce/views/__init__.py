from ecommerce.views.resources.invoice_item_views import (
    InvoiceItemRetrieveUpdateDestroyAPIView
)
from ecommerce.views.resources.invoice_views import (
    InvoiceListCreateAPIView,
    InvoiceRetrieveDestroyAPIView,
    InvoiceRetrieveUpdateBillingAddressAPIView,
    InvoiceRetrieveUpdateShippingAddressAPIView
)
from ecommerce.views.resources.onboarding_calculator_func_views import OnboardingCalculatorFuncAPIView
from ecommerce.views.resources.onboarding_submission_func_views import OnboardingSubmissionFuncAPIView
from ecommerce.views.resources.onboarding_validator_func_views import OnboardingValidatorFuncAPIView;
from ecommerce.views.resources.purchase_validator_func_views import PurchaseValidatorFuncAPIView;
from ecommerce.views.resources.invoice_func_views import InvoiceCalculationFuncView
from ecommerce.views.resources.stripe_event_views import PaymentEventAPIView
from ecommerce.views.gui.email_views import receipt_email_page
