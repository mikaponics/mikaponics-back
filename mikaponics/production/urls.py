from django.urls import path

from production.views.resource_views.production_retrieve_update_view import *
from production.views.resource_views.crop_data_sheet_list_view import *
from production.views.resource_views.crop_life_cycle_stage_list_view import *
from production.views.resource_views.crop_substrate_list_view import *
from production.views.resource_views.production_list_create_view import *
# from production.views.resource_views.production_termination_view import *
from production.views.resource_views.production_crop_retrieve_update_views import *
from production.views.resource_views.production_inspection_retrieve_update_view import *
from production.views.resource_views.production_crop_inspection_retrieve_update_view import *
from production.views.resource_views.production_inspection_list_create_view import *


urlpatterns = (
    path('api/crop-life-cycle-stages',
        CropLifeCycleStageListAPIView.as_view(),
        name='mikaponics_crop_life_cycle_stage_list_api_endpoint'
    ),
    path('api/crop-data-sheets',
        CropDataSheetListAPIView.as_view(),
        name='mikaponics_crop_data_sheet_list_api_endpoint'
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
    path('api/production-crop/<str:slug>',
        ProductionCropRetrieveUpdateAPIView.as_view(),
        name='mikaponics_production_retrieve_update_api_endpoint'
    ),
    # path('api/production-termination/<str:slug>',
    #     ProductionTerminationAPIView.as_view(),
    #     name='mikaponics_production_termination_api_endpoint'
    # ),
    path('api/production-inspections',
        ProductionInspectionListCreateAPIView.as_view(),
        name='mikaponics_production_inspection_list_create_api_endpoint'
    ),
    path('api/production-inspection/<str:slug>',
        ProductionInspectionRetrieveUpdateAPIView.as_view(),
        name='mikaponics_production_inspection_retrieve_update_api_endpoint'
    ),
    path('api/production-crop-inspection/<str:slug>',
        ProductionCropInspectionRetrieveUpdateAPIView.as_view(),
        name='mikaponics_production_crop_inspection_retrieve_update_api_endpoint'
    ),
)
