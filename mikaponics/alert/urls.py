from django.urls import path

from alert.views import *


urlpatterns = (
    path('email/production-alert/<int:pk>',
        ProductionAlertEmailWebBrowserView.as_view(),
        name='mikaponics_production_alert_items_email'
    ),
    path('email/instrument-alert/<int:pk>',
        InstrumentAlertEmailWebBrowserView.as_view(),
        name='mikaponics_instrument_alert_items_email'
    ),
    ############################################################################
    path('api/alerts',
        AlertItemsListAPIView.as_view(),
        name='mikaponics_alert_item_list_api_endpoint'
    ),
    path('api/alert/<str:slug>',
        AlertItemRetrieveAPIView.as_view(),
        name='mikaponics_alert_item_detail_api_endpoint'
    ),
    path('api/alert-was-viewed/<str:slug>',
        AlertItemWasViewedFuncAPIView.as_view(),
        name='mikaponics_alert_item_was_viewed_func_api_endpoint'
    ),
)
