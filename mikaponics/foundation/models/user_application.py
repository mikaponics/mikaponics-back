# -*- coding: utf-8 -*-
import uuid
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.contrib.postgres.indexes import BrinIndex
from django.db import models
from django.db import transaction
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from oauth2_provider.models import (
    Application,
    AbstractApplication
)


class UserApplicationManager(models.Manager):
    def full_text_search(self, keyword):
        """Function performs full text search of various textfields."""
        # The following code will use the native 'PostgreSQL' library
        # which comes with Django to utilize the 'full text search' feature.
        # For more details please read:
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/search/
        return UserApplication.objects.annotate(
            search=SearchVector('name', 'description',),
        ).filter(search=keyword)

    def delete_all(self):
        for obj in UserApplication.objects.iterator(chunk_size=500):
            obj.delete()


class UserApplication(models.Model):
    """
    Model used to track the user applications that exist in our system. The
    applications are `OAuth 2.0 Client credentials`. When an object gets created
    then this class will automatically create out `Application` model and
    when the object gets deleted then the `Application` gets deleted in the
    `foundation/signals.py` code.

    This file is dependent on the `Django OAuth Toolkit` so if there is anything
    not understood then please visit the library documentation via the link:
    https://django-oauth-toolkit.readthedocs.io/en/latest/index.html
    """

    '''
    Metadata
    '''

    class Meta:
        app_label = 'foundation'
        db_table = 'mika_user_applications'
        verbose_name = _('User Application')
        verbose_name_plural = _('User Applications')
        default_permissions = ()
        permissions = ()

    '''
    Constants & Choices
    '''

    '''
    Object Managers
    '''

    objects = UserApplicationManager()

    '''
    Fields
    '''

    id = models.BigAutoField(
        _("ID"),
        primary_key=True,
    )

    #
    #  FIELDS
    #

    uuid = models.UUIDField(
        help_text=_('The unique identifier used by us to identify our OAuth application.'),
        default=uuid.uuid4,
        null=False,
        editable=False,
        db_index=True,
        unique=True,
    )
    user = models.ForeignKey(
        'User',
        help_text=_('The user whom this application belongs to.'),
        related_name="user_applications",
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique slug used for this application when accessing details page.'),
        max_length=127,
        blank=True,
        null=False,
        db_index=True,
        unique=True,
        editable=False,
    )
    name = models.CharField(
        _("Name"),
        max_length=63,
        help_text=_('The name of this application.'),
    )
    description = models.TextField(
        _("Description"),
        help_text=_('A a description of this application.'),
    )

    #
    #  SYSTEM FIELDS
    #

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        'User',
        help_text=_('The user whom created this application.'),
        related_name="created_user_applications",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    created_from = models.GenericIPAddressField(
        _("Created from"),
        help_text=_('The IP address of the creator.'),
        blank=True,
        null=True
    )
    created_from_is_public = models.BooleanField(
        _("Is the IP "),
        help_text=_('Is creator a public IP and is routable.'),
        default=False,
        blank=True
    )
    last_modified_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        'User',
        help_text=_('The user whom last modified this application.'),
        related_name="last_modified_user_applications",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    last_modified_from = models.GenericIPAddressField(
        _("Last modified from"),
        help_text=_('The IP address of the modifier.'),
        blank=True,
        null=True
    )
    last_modified_from_is_public = models.BooleanField(
        _("Is the IP "),
        help_text=_('Is modifier a public IP and is routable.'),
        default=False,
        blank=True
    )

    '''
    Methods
    '''

    def __str__(self):
        return str(self.slug)

    def save(self, *args, **kwargs):
        """
        Override the save function so we can add extra functionality.

        (1) If we created the object then we will generate a custom slug.
        (a) If user exists then generate slug based on user's name.
        (b) Else generate slug with random string.
        (c) Create our OAuth 2.0 Authorization Application.
        """
        if not self.slug:
            count = UserApplication.objects.filter(user=self.user).count()
            count += 1

            # Generate our slug.
            self.slug = slugify(self.user)+"-application-"+str(count)

            # If a unique slug was not found then we will keep searching
            # through the various slugs until a unique slug is found.
            while UserApplication.objects.filter(slug=self.slug).exists():
                self.slug = slugify(self.user)+"-application-"+str(count)+"-"+get_random_string(length=8)

            # DEVELOPERS NOTE:
            # (1) We will be creating our OAuth 2.0 application here.
            # (2) We will be creating only a `confidential grant client credentials`
            #     type of OAuth 2.0 authorization.
            # (3) While the `Django OAuth2 Toolkil` library supports creating
            #     custom models using inheritence (see link: https://django-oauth-toolkit.readthedocs.io/en/latest/advanced_topics.html#extending-the-application-model)
            #     we will avoid and just map the two models using a `uuid` value.
            #     We are doing this to keep things simple.
            application, created = Application.objects.update_or_create(
                name=str(self.uuid),
                defaults={
                    "user": self.user,
                    "name": str(self.uuid),
                    "skip_authorization": True,
                    "authorization_grant_type": AbstractApplication.GRANT_CLIENT_CREDENTIALS,
                    "client_type": AbstractApplication.CLIENT_CONFIDENTIAL
                }
            )

        super(UserApplication, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return "/application/"+str(self.slug)
