from django.conf.urls import include, url
from django.views.generic.base import RedirectView

from account import views
from account import resources


urlpatterns = (
    ############################################################################
    url(r'^activate-email/(.*)/$',
        views.user_activation_email_page,
        name='mikaponics_activate_email'
    ),
    url(r'^reset-password-email/(.*)/$',
        views.reset_password_email_page,
        name='mikaponics_reset_password_email'
    ),
    url(r'^user-was-created-email/(.*)/$',
        views.user_was_created_email_page,
        name='mikaponics_user_was_created_email'
    ),
    ############################################################################
    # Authentication.
    url(r'^api/activate$', resources.ActivateAPIView.as_view(), name='mikaponics_activate_api_endpoint'),
    url(r'^api/logout$', resources.LogoutAPIView.as_view(), name='mikaponics_logout_api_endpoint'),
    url(r'^api/login$', resources.LoginAPIView.as_view(), name='mikaponics_login_api_endpoint'),
    url(r'^api/register$', resources.RegisterAPIView.as_view(), name='mikaponics_register_api_endpoint'),
    # url(r'^api/logout$', LogoutAPIView.as_view(), name='mikaponics_logout_api_endpoint'),
    url(r'^api/reset-password$', resources.ResetPasswordAPIView.as_view(), name='mikaponics_reset_password_api_endpoint'),
    url(r'^api/send-password-reset$', resources.SendPasswordResetAPIView.as_view(), name='mikaponics_send_password_reset_api_endpoint'),
    # Profile
    url(r'^api/profile$', resources.ProfileInfoRetrieveUpdateAPIView.as_view(), name='mikaponics_profile_info_api_endpoint'),
    url(r'^api/profile-with-token-refresh$', resources.RefreshTokenAPIView.as_view(), name='mikaponics_profile_info_with_token_refresh_api_endpoint'),
    ############################################################################
)
