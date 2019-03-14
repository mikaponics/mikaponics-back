
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include # This needs to be added

urlpatterns = ([
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('django-rq/', include('django_rq.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),
])

# Add support for language specific context URLs.
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    prefix_default_language=True
)
