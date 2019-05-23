from django.urls import path

from task.views import *


urlpatterns = (
    # path('email/production-task/<int:pk>',
    #     ProductionTaskEmailWebBrowserView.as_view(),
    #     name='mikaponics_production_task_items_email'
    # ),
    # path('email/instrument-task/<int:pk>',
    #     InstrumentTaskEmailWebBrowserView.as_view(),
    #     name='mikaponics_instrument_task_items_email'
    # ),
    # ############################################################################
    path('api/tasks',
        TaskItemsListAPIView.as_view(),
        name='mikaponics_task_item_list_api_endpoint'
    ),
    path('api/task/<str:slug>',
        TaskItemRetrieveAPIView.as_view(),
        name='mikaponics_task_item_detail_api_endpoint'
    ),
)
