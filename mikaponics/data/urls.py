from django.urls import path

from data import views


urlpatterns = (
    path(
        'api/data',
        views.TimeSeriesDataListCreateAPIView.as_view(),
        name='mikaponics_list_create_time_series_data_api_endpoint'
    ),
    path(
        'api/image-data',
        views.TimeSeriesImageDataListCreateAPIView.as_view(),
        name='mikaponics_list_create_time_series_image_data_api_endpoint'
    ),
)
