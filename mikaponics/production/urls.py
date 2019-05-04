from django.urls import path

from production.views.resource_views import *


urlpatterns = (
    path('api/productions',
        ProductionListCreateAPIView.as_view(),
        name='mikaponics_production_list_create_api_endpoint'
    ),
)
