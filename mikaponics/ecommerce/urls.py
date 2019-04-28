from django.urls import path

from ecommerce import views


urlpatterns = (
    ############################################################################
    path('invoice-receipt-email/<int:pk>',
        views.receipt_email_page,
        name='mikaponics_invoice_receipt_email'
    ),
    ############################################################################
    # --- ONBOARDING ---
    path('api/onboarding',
        views.OnboardingAPIView.as_view(),
        name='mikaponics_onboard_invoice_api_endpoint'
    ),

    # --- DEVICE PURCHASE ---
    path('api/device-purchase',
        views.DevicePurchaseAPIView.as_view(),
        name='mikaponics_device_purchase_api_endpoint'
    ),

    # --- INVOICE ---
    path('api/invoices',
        views.InvoiceListCreateAPIView.as_view(),
        name='mikaponics_invoices_list_create_api_endpoint'
    ),
    path('api/invoice/<str:slug>',
        views.InvoiceRetrieveDestroyAPIView.as_view(),
        name='mikaponics_invoices_retrieve_update_destroy_api_endpoint'
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

    # --- WEBHOOK ---
    path('api/stripe/webhook/',
        views.PaymentEventAPIView.as_view(),
        name='mikaponics_stripe_event_api_endpoint'
    ),
)
