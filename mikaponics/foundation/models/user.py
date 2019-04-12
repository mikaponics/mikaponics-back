# -*- coding: utf-8 -*-
"""user.py

The class model to represent the user in our application. This class overrides
default ``User`` model provided by ``Django`` to support the following:

TODO
"""
from __future__ import unicode_literals
import stripe
from datetime import date, datetime, timedelta
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields import JSONField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.functional import cached_property
from faker import Faker
from starterkit.utils import (
    get_random_string,
    generate_hash
)
from foundation import constants


stripe.api_key = settings.STRIPE_SECRET_KEY


def get_expiry_date(days=2):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):  #TODO: UNIT TEST
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):  #TODO: UNIT TEST
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):  #TODO: UNIT TEST
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def delete_all(self):
        try:
            for user in User.objects.iterator(chunk_size=500):
                user.delete()
        except Exception as e:
            print(e)

    def seed(self, length=25):
        results = []
        faker = Faker('en_CA')
        for i in range(0,length):
            try:
                user = User.objects.create(
                    email = faker.safe_email(),
                    first_name = faker.first_name(),
                    middle_name = None,
                    last_name = faker.last_name(),
                    birthdate = None,
                    nationality = None,
                    gender = None,
                    billing_email = faker.safe_email(),
                    billing_telephone = faker.msisdn(),
                    billing_country = faker.country(),
                    billing_locality = faker.city(),
                    billing_region = faker.province(),
                    # billing_post_office_box_number = faker.
                    billing_postal_code = faker.postalcode(),
                    billing_street_address = faker.street_address(),
                    # billing_street_address_extra = faker.
                    shipping_email = faker.safe_email(),
                    shipping_telephone = faker.msisdn(),
                    shipping_country = faker.country(),
                    shipping_locality = faker.city(),
                    shipping_region = faker.province(),
                    # shipping_post_office_box_number = faker.
                    shipping_postal_code = faker.postalcode(),
                    shipping_street_address = faker.street_address(),
                    # shipping_street_address_extra = faker.
                )
                results.append(user)
            except Exception as e:
                pass
        return results


class User(AbstractBaseUser, PermissionsMixin):

    '''
    Constants & choices
    '''

    class SUBSCRIPTION_STATUS:
        '''
        https://stripe.com/docs/billing/lifecycle
        '''
        NOT_INTERESTED = 'not_interested' # Our own addition.
        TRAILING = 'tracking'
        ACTIVE = 'active'
        PAST_DUE = 'past_due'
        CANCELED = 'canceled'
        UNPAID = 'unpaid'

    SUBSCRIPTION_STATUS_CHOICES = (
        (SUBSCRIPTION_STATUS.NOT_INTERESTED, _('Not Interested')),
        (SUBSCRIPTION_STATUS.TRAILING, _('Trailing')),
        (SUBSCRIPTION_STATUS.ACTIVE, _('Active')),
        (SUBSCRIPTION_STATUS.PAST_DUE, _('Past Due')),
        (SUBSCRIPTION_STATUS.CANCELED, _('Canceled')),
        (SUBSCRIPTION_STATUS.UNPAID, _('Unpaid')),
    )

    class REPORT_EMAIL_FREQUENCY:
        NEVER = 1
        WEEKLY = 2
        MONTHLY = 3

    REPORT_EMAIL_FREQUENCY_CHOICES = (
        (REPORT_EMAIL_FREQUENCY.NEVER, _('Never')),
        (REPORT_EMAIL_FREQUENCY.WEEKLY, _('Weekly')),
        (REPORT_EMAIL_FREQUENCY.MONTHLY, _('Monthly')),
    )

    '''
    Fields
    '''

    #
    # SYSTEM UNIQUE IDENTIFIER
    #
    email = models.EmailField( # THIS FIELD IS REQUIRED.
        _("Email"),
        help_text=_('Email address.'),
        db_index=True,
        unique=True
    )

    #
    # PERSON FIELDS - http://schema.org/Person
    #
    first_name = models.CharField(
        _("First Name"),
        max_length=63,
        help_text=_('The users given name.'),
        blank=True,
        null=True,
        db_index=True,
    )
    middle_name = models.CharField(
        _("Middle Name"),
        max_length=63,
        help_text=_('The users middle name.'),
        blank=True,
        null=True,
        db_index=True,
    )
    last_name = models.CharField(
        _("Last Name"),
        max_length=63,
        help_text=_('The users last name.'),
        blank=True,
        null=True,
        db_index=True,
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    birthdate = models.DateField(
        _('Birthdate'),
        help_text=_('The users birthdate.'),
        blank=True,
        null=True
    )
    nationality = models.CharField(
        _("Nationality"),
        max_length=63,
        help_text=_('Nationality of the person.'),
        blank=True,
        null=True,
    )
    gender = models.CharField(
        _("Gender"),
        max_length=63,
        help_text=_('Gender of the person. While Male and Female may be used, text strings are also acceptable for people who do not identify as a binary gender.'),
        blank=True,
        null=True,
    )

    #
    # Billing Address Fields
    #

    billing_email = models.EmailField(
        _("Billing Email"),
        max_length=127,
        help_text=_('The email used for billing'),
        blank=True,
        null=True,
    )
    billing_telephone = models.CharField(
        _("Billing Telephone"),
        help_text=_('The telephone number used for billing.'),
        blank=True,
        null=True,
        max_length=31,
    )
    billing_country = models.CharField(
        _("Billing Country"),
        max_length=127,
        help_text=_('The country. For example, USA. You can also provide the two-letter <a href="https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements">ISO 3166-1 alpha-2</a> country code.'),
        blank=True,
        null=True,
    )
    billing_locality = models.CharField(
        _("Billing Locality"),
        max_length=127,
        help_text=_('The locality. For example, Mountain View.'),
        blank=True,
        null=True,
    )
    billing_region = models.CharField(
        _("Billing Region"),
        max_length=127,
        help_text=_('The region. For example, CA.'),
        blank=True,
        null=True,
    )
    billing_post_office_box_number = models.CharField(
        _("Billing Post Office Box Number"),
        max_length=255,
        help_text=_('Apartment, suite, unit, building, floor, etc.'),
        blank=True,
        null=True,
    )
    billing_postal_code = models.CharField(
        _("Billing Postal Code"),
        max_length=127,
        help_text=_('The postal code. For example, 94043.'),
        db_index=True,
        blank=True,
        null=True,
    )
    billing_street_address = models.CharField(
        _("Billing Street Address"),
        max_length=255,
        help_text=_('The street address. For example, 1600 Amphitheatre Pkwy.'),
        blank=True,
        null=True,
    )
    billing_street_address_extra = models.CharField(
        _("Billing Street Address (Extra Line)"),
        max_length=255,
        help_text=_('Apartment, suite, unit, building, floor, etc.'),
        blank=True,
        null=True,
    )

    #
    # Shipping Address Fields
    #

    shipping_email = models.EmailField(
        _("Shipping Email"),
        max_length=127,
        help_text=_('The email used for shipping.'),
        blank=True,
        null=True,
    )
    shipping_telephone = models.CharField(
        _("Shipping Telephone"),
        help_text=_('The number used for shipper.'),
        blank=True,
        null=True,
        max_length=31,
    )
    shipping_country = models.CharField(
        _("Shipping Country"),
        max_length=127,
        help_text=_('The country. For example, USA. You can also provide the two-letter <a href="https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements">ISO 3166-1 alpha-2</a> country code.'),
        blank=True,
        null=True,
    )
    shipping_locality = models.CharField(
        _("Shipping Locaility"),
        max_length=127,
        help_text=_('The locality. For example, Mountain View.'),
        blank=True,
        null=True,
    )
    shipping_region = models.CharField(
        _("Shipping Region"),
        max_length=127,
        help_text=_('The region. For example, CA.'),
        blank=True,
        null=True,
    )
    shipping_post_office_box_number = models.CharField(
        _("Shipping Post Office Box Number"),
        max_length=127,
        help_text=_('Apartment, suite, unit, building, floor, etc.'),
        blank=True,
        null=True,
    )
    shipping_postal_code = models.CharField(
        _("Shipping Postal Code"),
        max_length=127,
        help_text=_('The postal code. For example, 94043.'),
        db_index=True,
        blank=True,
        null=True,
    )
    shipping_street_address = models.CharField(
        _("Shipping Street Address"),
        max_length=255,
        help_text=_('The street address. For example, 1600 Amphitheatre Pkwy.'),
        blank=True,
        null=True,
    )
    shipping_street_address_extra = models.CharField(
        _("Shipping Street Address (Extra Line)"),
        max_length=255,
        help_text=_('Apartment, suite, unit, building, floor, etc.'),
        blank=True,
        null=True,
    )

    #
    # SYSTEM FIELD
    #

    timezone = models.CharField(
        _("Timezone"),
        max_length=63,
        help_text=_('The timezone the user belongs to.'),
        blank=True,
        default='UTC',
    )
    report_email_frequency = models.PositiveSmallIntegerField(
        _("Report email frequency"),
        help_text=_('The frequency to email the report by.'),
        blank=True,
        null=False,
        default=REPORT_EMAIL_FREQUENCY.WEEKLY,
        choices=REPORT_EMAIL_FREQUENCY_CHOICES,
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        blank=True
    )
    is_staff = models.BooleanField(
        _('Is Staff'),
        default=False,
        blank=True
    )
    is_superuser = models.BooleanField(
        _('Is Superuser'),
        default=False,
        blank=True
    )
    salt = models.CharField( #DEVELOPERS NOTE: Used for cryptographic signatures.
        _("Salt"),
        max_length=127,
        help_text=_('The unique salt value me with this object.'),
        default=generate_hash,
        unique=True,
        blank=True,
        null=True
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of user this is. Value represents ID of user type.'),
        default=0,
        blank=True,
        db_index=True,
    )
    is_ok_to_email = models.BooleanField(
        _("Is OK to email"),
        help_text=_('Indicates whether customer allows being reached by email'),
        default=True,
        blank=True
    )
    is_ok_to_text = models.BooleanField(
        _("Is OK to text"),
        help_text=_('Indicates whether customer allows being reached by text.'),
        default=True,
        blank=True
    )
    location = PointField(
        _("Location"),
        help_text=_('A longitude and latitude coordinates of this location.'),
        null=True,
        blank=True,
        srid=4326,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    #
    # STRIPE FIELDS
    #

    customer_id = models.CharField(
        _("Customer ID"),
        max_length=127,
        help_text=_('The customer ID from the payment merchant.'),
        blank=True,
        null=True,
    )
    customer_data = JSONField(
        _("Customer Data"),
        help_text=_('The customer details from the payment merchant.'),
        blank=True,
        null=True,
    )
    subscription_status = models.CharField(
        _("Subscription Status"),
        help_text=_('The customer subscription status from the payment merchant.'),
        max_length=15,
        blank=False,
        null=False,
        default=SUBSCRIPTION_STATUS.NOT_INTERESTED,
        choices=SUBSCRIPTION_STATUS_CHOICES,
    )
    subscription_plan = models.ForeignKey(
        "SubscriptionPlan",
        help_text=_('The subscription plan this user is enrolled in.'),
        blank=True,
        null=True,
        related_name="users",
        on_delete=models.SET_NULL,
        editable=False, # Only device or web-app can change this state, not admin user!
    )
    subscription_data = JSONField(
        _("Subscription Data"),
        help_text=_('The subscription details from the payment merchant.'),
        blank=True,
        null=True,
    )


    #
    # EMAIL ACTIVATION FIELD
    #

    was_email_activated = models.BooleanField(
        _("Was Email Activated"),
        help_text=_('Was the email address verified?'),
        default=False,
        blank=True
    )

    #
    # ONBOARDING FIELD
    #

    was_onboarded = models.BooleanField(
        _("Was Onboarded"),
        help_text=_('Was the user onboarded in our system? If yes then allow user access to their dashboard and the remaining features of the site.'),
        default=False,
        blank=True
    )
    onboarding_survey_data = JSONField(
        _("Survey data"),
        help_text=_('The onboarding submitted survey data.'),
        blank=True,
        null=True,
    )

    #
    # PASSWORD RESET FIELDS
    #

    pr_access_code = models.CharField(
        _("Password Reset Access Code"),
        max_length=127,
        help_text=_('The access code to enter the password reset page to be granted access to restart your password.'),
        blank=True,
        default=generate_hash,
    )
    pr_expiry_date = models.DateTimeField(
        _('Password Reset Access Code Expiry Date'),
        help_text=_('The date where the access code expires and no longer works.'),
        blank=True,
        default=get_expiry_date,
    )

    objects = UserManager()

    # DEVELOPERS NOTE:
    # WE WILL BE USING "EMAIL" AND "ACADEMY" AS THE UNIQUE PAIR THAT WILL
    # DETERMINE WHETHER THE AN ACCOUNT EXISTS. WE ARE DOING THIS TO SUPPORT
    # TENANT SPECIFIC USER ACCOUNTS WHICH DO NOT EXIST ON OTHER TENANTS.
    # WE USE CUSTOM "AUTHENTICATION BACKEND" TO SUPPORT THE LOGGING IN.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'is_staff',
        'is_active',
        'is_superuser',
    ]

    class Meta:
        app_label = 'foundation'
        db_table = 'mika_users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        default_permissions = ()
        permissions = ()

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name  #TODO: UNIT TEST

    def __str__(self):
        return self.get_full_name()

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)  #TODO: UNIT TEST

    def generate_pr_code(self):
        """
        Function generates a new password reset code and expiry date.
        """
        self.pr_access_code = get_random_string(length=127)
        self.pr_expiry_date = get_expiry_date()
        self.save()
        return self.pr_access_code

    def has_pr_code_expired(self):
        """
        Returns true or false depending on whether the password reset code
        has expired or not.
        """
        today = timezone.now()
        return today >= self.pr_expiry_date

    @cached_property
    def draft_invoice(self):
        """
        Returns a single invoice which has been opened and is ready for the
        user to add products to purchase. If no draft invoice was returned then
        we will create one and return it here.
        """
        from foundation.models.invoice import Invoice
        from foundation.models.store import Store
        from foundation.models.shipper import Shipper
        store = Store.objects.default_store

        # # For debugging purposes only.
        # print("STORE:", store)
        # print("STATE:", Invoice.ORDER_STATE.DRAFT)
        # print("USER:", self)

        # Attempt to find our invoice for the specific criteria.
        invoice = Invoice.objects.filter(
            store=store,
            state=Invoice.ORDER_STATE.DRAFT,
            user=self
        ).order_by('created_at').first()

        # If our attempt failed then we generate our invoice here, else we
        # return the invoice we originally found.
        if invoice is None:
            invoice = Invoice.objects.create(
                store=store,
                user=self,
                state=Invoice.ORDER_STATE.DRAFT,
                shipper=Shipper.objects.all().first(),
                slug=None
            )
        return invoice

    def invalidate(self, method_name):
        """
        Function used to clear the cache for the cached property functions.
        """
        try:
            if method_name == 'draft_invoice':
                del self.draft_invoice
            else:
                raise Exception("Method name not found.")
        except AttributeError:
            pass
