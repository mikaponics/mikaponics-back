from django.urls import path

from alert.views import *


urlpatterns = (
    ############################################################################
    path('email/instrument-alert/<int:pk>',
        AlertEmailWebBrowserView.as_view(),
        name='mikaponics_instrument_alerts_email'
    ),
    path('api/instrument-alerts',
        InstrumentAlertsListAPIView.as_view(),
        name='mikaponics_instrument_alerts_list_api_endpoint'
    ),
    path('api/instrument-alert/<str:slug>',
        InstrumentAlertRetrieveAPIView.as_view(),
        name='mikaponics_instrument_alert_detail_api_endpoint'
    ),
)
