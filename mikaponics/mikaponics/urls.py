
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include # This needs to be added

urlpatterns = ([
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('django-rq/', include('django_rq.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),

    # Allow the following apps for being accessed without language string.
    path('', include('account.urls')),
    path('', include('dashboard.urls')),
    path('', include('device.urls')),
    path('', include('instrument.urls')),
    path('', include('ecommerce.urls')),
    path('', include('alert.urls')),
    path('', include('foundation.urls')),
    path('', include('production.urls')),
    path('', include('task.urls')),
    path('', include('data.urls')),
])

# Add support for language specific context URLs.
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('account.urls')),
    path('', include('dashboard.urls')),
    path('', include('device.urls')),
    path('', include('instrument.urls')),
    path('', include('ecommerce.urls')),
    path('', include('alert.urls')),
    path('', include('foundation.urls')),
    path('', include('production.urls')),
    path('', include('task.urls')),
    path('', include('data.urls')),
    prefix_default_language=True
)
