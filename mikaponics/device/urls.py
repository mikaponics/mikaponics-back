from django.urls import path

from device import views


urlpatterns = (
    path('api/devices', views.DeviceListCreateAPIView.as_view(), name='mikaponics_list_create_device_api_endpoint'),
    path('api/device-authorize', views.DeviceAuthorizeAPIView.as_view(), name='mikaponics_device_authorization_api_endpoint'),
    path('api/device/<str:slug>', views.DeviceRetrieveUpdateDestroyAPIView.as_view(), name='mikaponics_retrieve_update_destroy_device_api_endpoint'),
    path('api/device/<str:slug>/profile', views.DeviceProfileAPIView.as_view(), name='mikaponics_device_profile_api_endpoint'),
)
