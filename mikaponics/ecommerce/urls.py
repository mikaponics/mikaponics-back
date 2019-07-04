from django.urls import path

from ecommerce import views


urlpatterns = (
    ############################################################################
    path('invoice-receipt-email/<int:pk>',
        views.receipt_email_page,
        name='mikaponics_invoice_receipt_email'
    ),
    path('onboarded-email/<int:pk>',
        views.onboarded_email_page,
        name='mikaponics_onboarded_email'
    ),
    ############################################################################
    # --- FINANCIAL TRANSACTIONS ---
    path('api/purchase',
        views.PurchaseAPIView.as_view(),
        name='mikaponics_purchase_api_endpoint'
    ),
    path('api/products',
        views.ProductListAPIView.as_view(),
        name='mikaponics_product_list_api_endpoint'
    ),
    path('api/subscription',
        views.SubscriptionAPIView.as_view(),
        name='mikaponics_subscription_api_endpoint'
    ),
    path('api/calculate-purchase-device-receipt',
        views.CalculatePurchaseDeviceFuncAPIView.as_view(),
        name='mikaponics_calculate_purchase_device_receipt_api_endpoint'
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
    path('api/invoice-send-email/<str:slug>',
        views.InvoiceSendEmailAPIView.as_view(),
        name='mikaponics_invoice_send_email_api_endpoint'
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
