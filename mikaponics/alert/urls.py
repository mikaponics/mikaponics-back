from django.urls import path

from alert.views import *


urlpatterns = (
    ############################################################################
    path('email/instrument-alert/<int:pk>',
        AlertEmailWebBrowserView.as_view(),
        name='mikaponics_instrument_alerts_email'
    ),

)
