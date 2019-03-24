from django.urls import path

from ecommerce import views


urlpatterns = (
    ############################################################################
    path('invoice-receipt-email/<int:pk>',
        views.receipt_email_page,
        name='mikaponics_invoice_receipt_email'
    ),
    ############################################################################
    path('api/onboarding/validation',
        views.OnboardingValidatorFuncAPIView.as_view(),
        name='mikaponics_onboarding_validator_func_api_endpoint'
    ),
    path('api/onboarding/calculator',
        views.OnboardingCalculatorFuncAPIView.as_view(),
        name='mikaponics_onboarding_calculator_func_api_endpoint'
    ),
    path('api/onboarding/submission',
        views.OnboardingSubmissionFuncAPIView.as_view(),
        name='mikaponics_onboarding_submission_func_api_endpoint'
    ),
    path('api/purchase-validation',
        views.PurchaseValidatorFuncAPIView.as_view(),
        name='mikaponics_purchase_validator_func_api_endpoint'
    ),
    path('api/invoice/<int:pk>/calculate',
        views.InvoiceCalculationFuncView.as_view(),
        name='mikaponics_purchase_validator_func_api_endpoint'
    ),
    path('api/invoice/<int:pk>/shipping-address',
        views.InvoiceRetrieveUpdateShippingAddressAPIView.as_view(),
        name='mikaponics_invoice_item_retrieve_update_shipping_address_destroy_api_endpoint'
    ),
    path('api/invoice-item/<int:pk>',
        views.InvoiceItemRetrieveUpdateDestroyAPIView.as_view(),
        name='mikaponics_invoice_item_retrieve_update_destroy_api_endpoint'
    ),
    path('api/invoice/<int:pk>/billing-address',
        views.InvoiceRetrieveUpdateBillingAddressAPIView.as_view(),
        name='mikaponics_invoice_item_retrieve_update_billing_address_destroy_api_endpoint'
    ),
    path('api/stripe/webhook/',
        views.PaymentEventAPIView.as_view(),
        name='mikaponics_stripe_event_api_endpoint'
    ),
)
