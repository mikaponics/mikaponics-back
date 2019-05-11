from django.urls import path

from production.views.resource_views.all_views import *
from production.views.resource_views.crop_list_view import *
from production.views.resource_views.crop_substrate_list_view import *
from production.views.resource_views.production_list_create_view import *
from production.views.resource_views.production_termination_view import *


urlpatterns = (
    path('api/crops',
        CropListAPIView.as_view(),
        name='mikaponics_crop_list_api_endpoint'
    ),
    path('api/crop-substrates',
        CropSubstrateListAPIView.as_view(),
        name='mikaponics_crop_substrates_list_api_endpoint'
    ),
    path('api/productions',
        ProductionListCreateAPIView.as_view(),
        name='mikaponics_production_list_create_api_endpoint'
    ),
    path('api/production/<str:slug>',
        ProductionRetrieveUpdateAPIView.as_view(),
        name='mikaponics_production_retrieve_update_api_endpoint'
    ),
    path('api/production-termination/<str:slug>',
        ProductionTerminationAPIView.as_view(),
        name='mikaponics_production_termination_api_endpoint'
    ),
)
