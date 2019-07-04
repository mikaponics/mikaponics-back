from ecommerce.serializers.product_serializers import ProductListSerializer
from ecommerce.serializers.invoice_list_create_serializers import InvoiceListCreateSerializer
from ecommerce.serializers.invoice_item_retrieve_update_destroy_serializers import (
    InvoiceItemRetrieveUpdateDestroySerializer,
)
from ecommerce.serializers.invoice_retrieve_update_destroy_serializers import (
    InvoiceRetrieveUpdateSerializer,
    InvoiceRetrieveUpdateBillingAddressSerializer,
    InvoiceRetrieveUpdateShippingAddressSerializer,
    InvoiceSendEmailSerializer
)
from ecommerce.serializers.stripe_event_serializers import PaymentEventSerializer
from ecommerce.serializers.onboarding_retrieve_serializers import OnboardingRetrieveSerializer
from ecommerce.serializers.onboarding_update_serializers import OnboardingUpdateSerializer
from ecommerce.serializers.purchase_device_list_retrieve_serializers import PurchaseDeviceInvoiceListSerializer
from ecommerce.serializers.purchase_device_list_retrieve_serializers import PurchaseDeviceRetrieveSerializer
from ecommerce.serializers.purchase_device_update_serializers import PurchaseDeviceUpdateSerializer
from ecommerce.serializers.subscription_crud_serializers import (
    SubscriptionRetrieveSerializer,
    SubscriptionUpdateSerializer
)
from ecommerce.serializers.calculate_purchase_device_func_serializer import CalculatePurchaseDeviceFuncSerializer
from ecommerce.serializers.purchase_process_serializers import PurchaseProcessSerializer
