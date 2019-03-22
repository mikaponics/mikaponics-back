from django.urls import path

from foundation import views


urlpatterns = (
    path('',
        views.index_view,
        name='mikaponics_index_view'
    ),
)
