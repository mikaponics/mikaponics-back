from django.urls import path

from instrument import views


urlpatterns = (
    path('api/data/csv',
        views.time_series_data_streaming_csv_view,
        name='mikaponics_download_data_api_endpoint'
    ),
    path('instrument/<int:pk>/alert-config',
        views.InstrumentAlertConfigRetrieveUpdateDestroyAPIView.as_view(),
        name='mikaponics_instrument_alert_config_api_endpoint'
    ),
    path('api/instruments',
        views.InstrumentListAPIView.as_view(),
        name='mikaponics_instrument_alert_config_api_endpoint'
    ),
    path('api/instrument/<str:slug>',
        views.InstrumentRetrieveUpdateAPIView.as_view(),
        name='mikaponics_instrument_retrieve_update_api_endpoint'
    ),
)
