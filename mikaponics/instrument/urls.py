from django.urls import path

from instrument import views


urlpatterns = (
    path('data/csv',
        views.time_series_data_streaming_csv_view,
        name='mikaponics_download_data_api_endpoint'
    ),
    path('instrument/<int:pk>/alert-config',
        views.InstrumentAlertConfigRetrieveUpdateDestroyAPIView.as_view(),
        name='mikaponics_instrument_alert_config_api_endpoint'
    ),
)
