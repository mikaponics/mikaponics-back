from django.urls import path

from device import views


urlpatterns = (
    path('api/devices', views.DeviceListCreateAPIView.as_view(), name='mikaponics_list_create_device_api_endpoint'),
    path('api/device/<str:device_uuid>/profile', views.DeviceProfileAPIView.as_view(), name='mikaponics_device_profile_api_endpoint'),
    path('api/device-operations/activate', views.DeviceActivateOperationAPIView.as_view(), name='mikaponics_device_activate_operation_api_endpoint'),
    path('api/device-operations/submit-data', views.DeviceInstrumentSetTimeSeriesDatumeOperationAPIView.as_view(), name='mikaponics_device_submit_dat_operation_api_endpoint'),
    path('api/data', views.TimeSeriesDataListCreateAPIView.as_view(), name='mikaponics_list_create_tsd_api_endpoint'),
)
