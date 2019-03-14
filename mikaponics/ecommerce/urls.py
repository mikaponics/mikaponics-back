from django.urls import path

from ecommerce import views


urlpatterns = (
    ############################################################################
    path('order-receipt-email/<int:pk>',
        views.receipt_email_page,
        name='mikaponics_order_receipt_email'
    ),
    ############################################################################
    path('purchase-step-1',
        views.create_purchase_master_page,
        name='mikaponics_purchase_step_1_master'
    ),
    path('purchase-step-2',
        views.create_purchase_step_2_page,
        name='mikaponics_purchase_step_2_master'
    ),
    path('purchase-step-3',
        views.create_purchase_step_3_page,
        name='mikaponics_purchase_step_3_master'
    ),
    path('purchase-step-4',
        views.create_purchase_step_4_page,
        name='mikaponics_purchase_step_4_master'
    ),
    path('purchase-finished',
        views.create_purchase_finished_step_page,
        name='mikaponics_create_purchase_finished_step_page'
    ),
    path('orders',
        views.list_orders_page,
        name='mikaponics_list_orders_master'
    ),
    path('orders/<int:pk>',
        views.order_detail_page,
        name='mikaponics_order_detail'
    ),
    ############################################################################
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
