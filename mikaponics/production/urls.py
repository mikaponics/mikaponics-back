from django.urls import path

from production.views.resource_views.all_views import *
from production.views.resource_views.crop_list_view import *

urlpatterns = (
    path('api/crops',
        CropListAPIView.as_view(),
        name='mikaponics_crop_list_api_endpoint'
    ),
    path('api/productions',
        ProductionListCreateAPIView.as_view(),
        name='mikaponics_production_list_create_api_endpoint'
    ),
    path('api/production/<str:slug>',
        ProductionRetrieveUpdateAPIView.as_view(),
        name='mikaponics_production_retrieve_update_api_endpoint'
    ),
)
