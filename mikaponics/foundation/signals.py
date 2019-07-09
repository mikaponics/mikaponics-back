from oauth2_provider.signals import app_authorized


"""
Why are we doing this? The reason is because ``django-oauth-toolkit`` does
not attach the user object to the authorized token when user specific
"client credentials" application gets authorized.
"""


def handle_app_authorized(sender, request, token, **kwargs):
    """
    Function will be fired whenever a new token was authorized. We are
    adding the following extra functionality:

        (1) If the ``application`` has a user associated with it then we will
            attach the user to the newely created token - if the token was not
            assigned the user!

        (2) This signal will fire on every oAuth 2.0 authorization request.
    """

    if token:
        if token.application:
            if token.application.user and token.user is None:
                token.user = token.application.user
                token.save()


app_authorized.connect(handle_app_authorized)


from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from oauth2_provider.models import (
    Application,
    AbstractApplication,
    # AbstractAccessToken,
    # AccessToken,
    # RefreshToken
)

from foundation.models import UserApplication, Device

@receiver(post_save, sender=Device)
def create_oauth_for_device(sender, instance, created, **kwargs):
    """
    Function will be fired whenever a new `Device` has been created. We do this
    because we want to automatically generate our `client credentials` oAuth 2.0
    authorization. We are doing this because we want to make setting up devices
    to be easier.
    """
    if created:
        application, created = Application.objects.update_or_create(
            name=str(instance.uuid),
            defaults={
                "user": instance.user,
                "name": str(instance.uuid),
                "skip_authorization": True,
                "authorization_grant_type": AbstractApplication.GRANT_CLIENT_CREDENTIALS,
                "client_type": AbstractApplication.CLIENT_CONFIDENTIAL
            }
        )

@receiver(post_delete, sender=Device)
def delete_oauth_for_device(sender, instance, **kwargs):
    """
    Function will be fired when a `Device` has been deleted. We want to
    automatically unauthorize the existing oAuth 2.0 authorization we have
    for that device.
    """
    if instance:
        Application.objects.filter(name=instance.uuid).delete()

@receiver(post_delete, sender=UserApplication)
def delete_oauth_for_user_application(sender, instance, **kwargs):
    """
    Function will be fired when a `Application` has been deleted. We want to
    automatically unauthorize the existing oAuth 2.0 authorization we have
    for that device.
    """
    if instance:
        Application.objects.filter(name=instance.uuid).delete()
