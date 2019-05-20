from django.urls import path

from alert.views import *


urlpatterns = (
    ############################################################################
    # path('email/instrument-alert/<int:pk>',
    #     AlertEmailWebBrowserView.as_view(),
    #     name='mikaponics_alert_items_email'
    # ),
    path('api/alerts',
        AlertItemsListAPIView.as_view(),
        name='mikaponics_alert_item_list_api_endpoint'
    ),
    path('api/alert/<str:slug>',
        AlertItemRetrieveAPIView.as_view(),
        name='mikaponics_alert_item_detail_api_endpoint'
    ),
)
