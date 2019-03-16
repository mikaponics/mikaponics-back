from django.urls import path

from ecommerce import views


urlpatterns = (
    ############################################################################
    path('order-receipt-email/<int:pk>',
        views.receipt_email_page,
        name='mikaponics_order_receipt_email'
    ),
    ############################################################################
    path('api/onboarding/validation',
        views.OnboardingValidatorFuncAPIView.as_view(),
        name='mikaponics_onboarding_validator_func_api_endpoint'
    ),
    path('api/purchase-validation',
        views.PurchaseValidatorFuncAPIView.as_view(),
        name='mikaponics_purchase_validator_func_api_endpoint'
    ),
    path('api/order/<int:pk>/calculate',
        views.OrderCalculationFuncView.as_view(),
        name='mikaponics_purchase_validator_func_api_endpoint'
    ),
    path('api/order/<int:pk>/shipping-address',
        views.OrderRetrieveUpdateShippingAddressAPIView.as_view(),
        name='mikaponics_order_item_retrieve_update_shipping_address_destroy_api_endpoint'
    ),
    path('api/order-item/<int:pk>',
        views.OrderItemRetrieveUpdateDestroyAPIView.as_view(),
        name='mikaponics_order_item_retrieve_update_destroy_api_endpoint'
    ),
    path('api/order/<int:pk>/billing-address',
        views.OrderRetrieveUpdateBillingAddressAPIView.as_view(),
        name='mikaponics_order_item_retrieve_update_billing_address_destroy_api_endpoint'
    ),
    path('api/stripe/webhook/',
        views.StripeEventAPIView.as_view(),
        name='mikaponics_stripe_event_api_endpoint'
    ),
)
