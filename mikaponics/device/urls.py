from django.urls import path

from device import views


urlpatterns = (
    #---------------------------------------------------------------------------
    path('device/<str:pk>/environment-variables-file',
        views.DeviceEnvironmentVariablesFileView.as_view(),
        name='mikaponics_device_environment_variable_file_detail'
    ),
    #---------------------------------------------------------------------------
    path('api/devices', views.DeviceListCreateAPIView.as_view(), name='mikaponics_list_create_device_api_endpoint'),
    path('api/device/<str:slug>', views.DeviceRetrieveUpdateDestroyAPIView.as_view(), name='mikaponics_retrieve_update_destroy_device_api_endpoint'),
    path('api/device/<str:device_uuid>/profile', views.DeviceProfileAPIView.as_view(), name='mikaponics_device_profile_api_endpoint'),
    path('api/device-operations/activate', views.DeviceActivateOperationAPIView.as_view(), name='mikaponics_device_activate_operation_api_endpoint'),
    path('api/device-operations/submit-data', views.DeviceInstrumentSetTimeSeriesDatumeOperationAPIView.as_view(), name='mikaponics_device_submit_dat_operation_api_endpoint'),
    path('api/data', views.TimeSeriesDataListCreateAPIView.as_view(), name='mikaponics_list_create_tsd_api_endpoint'),
)
