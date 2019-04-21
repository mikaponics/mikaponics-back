# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q, Prefetch, Sum
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from rest_framework import exceptions, serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator


logger = logging.getLogger(__name__)


def get_todays_date_plus_days(days=0):
    """Returns the current date plus paramter number of days."""
    return timezone.now() + timedelta(days=days)


class OnboardingValidatorFuncSerializer(serializers.Serializer):
    step_number = serializers.IntegerField(required=False)

    # STEP 1 OF 6:
    quantity = serializers.IntegerField(required=True)

    # STEP 2 OF 6:
    billing_given_name = serializers.CharField(required=True,allow_blank=False,)
    billing_last_name = serializers.CharField(required=True,allow_blank=False,)
    billing_address_country = serializers.CharField(required=True,allow_blank=False,)
    billing_address_region = serializers.CharField(required=True,allow_blank=False,)
    billing_address_locality = serializers.CharField(required=True,allow_blank=False,)
    billing_postal_code = serializers.CharField(required=True,allow_blank=False,)
    billing_street_address = serializers.CharField(required=True,allow_blank=False,)
    billing_postal_code = serializers.CharField(required=True,allow_blank=False,)
    billing_post_office_box_number = serializers.CharField(required=False,allow_blank=True,)
    billing_email = serializers.CharField(required=True,allow_blank=False,)
    billing_telephone = serializers.CharField(required=True,allow_blank=False,)

    # STEP 3 OF 6:
    shipping_given_name = serializers.CharField(required=True,allow_blank=False,)
    shipping_last_name = serializers.CharField(required=True,allow_blank=False,)
    shipping_address_country = serializers.CharField(required=True,allow_blank=False,)
    shipping_address_region = serializers.CharField(required=True,allow_blank=False,)
    shipping_address_locality = serializers.CharField(required=True,allow_blank=False,)
    shipping_postal_code = serializers.CharField(required=True,allow_blank=False,)
    shipping_street_address = serializers.CharField(required=True,allow_blank=False,)
    shipping_postal_code = serializers.CharField(required=True,allow_blank=False,)
    shipping_post_office_box_number = serializers.CharField(required=False,allow_blank=True,)
    shipping_email = serializers.CharField(required=True,allow_blank=False,)
    shipping_telephone = serializers.CharField(required=True,allow_blank=False,)

    # Meta Information.
    class Meta:
        fields = (
            'step_number',

            # STEP 1 OF 6:
            'quantity',

            # STEP 2 OF 6:
            'billing_given_name',
            'billing_last_name',
            'billing_address_country',
            'billing_address_region',
            'billing_address_locality',
            'billing_postal_code',
            'billing_street_address',
            'billing_postal_code',
            'billing_post_office_box_number',
            'billing_email',
            'billing_telephone',

            # STEP 3 OF 6:
            'shipping_given_name',
            'shipping_last_name',
            'shipping_address_country',
            'shipping_address_region',
            'shipping_address_locality',
            'shipping_postal_code',
            'shipping_street_address',
            'shipping_postal_code',
            'shipping_post_office_box_number',
            'shipping_email',
            'shipping_telephone',
        )

    def validate_quantity(self, data):
        quantity = data
        if quantity > 50:
            raise exceptions.ValidationError({
                'quantity': _('Cannot invoice more then 50 devices in one invoice, please contact <a href="mailto:info@mikaponics.com">info@mikasoftware.com</a> to invoice more.')
            })
        elif quantity == 0:
            raise exceptions.ValidationError({
                'quantity': _('Please invoice more then zero!')
            })
        elif quantity < 0:
            raise exceptions.ValidationError({
                'quantity': _('Please pick an invoice more then zero!')
            })
        return data

    # def validate_step2(self, data):
    #     billing_given_name = data.get('billing_given_name', "")
    #     billing_last_name = data.get('billing_last_name', "")
    #     billing_address_country = data.get('billing_address_country', "")
    #     billing_address_region = data.get('billing_address_region', "")
    #     billing_address_locality = data.get('billing_address_locality', "")
    #     billing_postal_code = data.get('billing_postal_code', "")
    #     billing_email = data.get('billing_email', "")
    #     billing_telephone = data.get('billing_telephone', "")
    #     if billing_given_name == "" or billing_given_name == None:
    #         raise exceptions.ValidationError({
    #             'billing_given_name': _('Please enter your first name.')
    #         })
    #     if billing_last_name == "" or billing_last_name == None:
    #         raise exceptions.ValidationError({
    #             'billing_last_name': _('Please enter your last name.')
    #         })
    #     if billing_address_country == "" or billing_address_country == None:
    #         raise exceptions.ValidationError({
    #             'billing_address_country': _('Please enter your country.')
    #         })
    #     if billing_address_region == "" or billing_address_region == None:
    #         raise exceptions.ValidationError({
    #             'billing_address_region': _('Please enter your state / province.')
    #         })
    #     if billing_address_locality == "" or billing_address_locality == None:
    #         raise exceptions.ValidationError({
    #             'billing_address_locality': _('Please enter your city.')
    #         })
    #     if billing_postal_code == "" or billing_postal_code == None:
    #         raise exceptions.ValidationError({
    #             'billing_postal_code': _('Please enter your state / zipcode.')
    #         })
    #     if billing_email == "" or billing_email == None:
    #         raise exceptions.ValidationError({
    #             'billing_email': _('Please enter your email.')
    #         })
    #     if billing_telephone == "" or billing_telephone == None:
    #         raise exceptions.ValidationError({
    #             'billing_telephone': _('Please enter your telephone.')
    #         })
    #
    # def validate_step3(self, data):
    #     shipping_given_name = data.get('shipping_given_name', "")
    #     shipping_last_name = data.get('shipping_last_name', "")
    #     shipping_address_country = data.get('shipping_address_country', "")
    #     shipping_address_region = data.get('shipping_address_region', "")
    #     shipping_address_locality = data.get('shipping_address_locality', "")
    #     shipping_postal_code = data.get('shipping_postal_code', "")
    #     shipping_email = data.get('shipping_email', "")
    #     shipping_telephone = data.get('shipping_telephone', "")
    #     if shipping_given_name == "" or shipping_given_name == None:
    #         raise exceptions.ValidationError({
    #             'shipping_given_name': _('Please enter your first name.')
    #         })
    #     if shipping_last_name == "" or shipping_last_name == None:
    #         raise exceptions.ValidationError({
    #             'shipping_last_name': _('Please enter your last name.')
    #         })
    #     if shipping_address_country == "" or shipping_address_country == None:
    #         raise exceptions.ValidationError({
    #             'shipping_address_country': _('Please enter your country.')
    #         })
    #     if shipping_address_region == "" or shipping_address_region == None:
    #         raise exceptions.ValidationError({
    #             'shipping_address_region': _('Please enter your state / province.')
    #         })
    #     if shipping_address_locality == "" or shipping_address_locality == None:
    #         raise exceptions.ValidationError({
    #             'shipping_address_locality': _('Please enter your city.')
    #         })
    #     if shipping_postal_code == "" or shipping_postal_code == None:
    #         raise exceptions.ValidationError({
    #             'shipping_postal_code': _('Please enter your state / zipcode.')
    #         })
    #     if shipping_email == "" or shipping_email == None:
    #         raise exceptions.ValidationError({
    #             'shipping_email': _('Please enter your email.')
    #         })
    #     if shipping_telephone == "" or shipping_telephone == None:
    #         raise exceptions.ValidationError({
    #             'shipping_telephone': _('Please enter your telephone.')
    #         })
    #
    # def validate_step4(self, data):
    #     print("TODO: Implement 4")
    #
    # def validate_step5(self, data):
    #     print("TODO: Implement 5")
    #
    # def validate_step6(self, data):
    #     print("TODO: Implement 6")

    # def validate(self, data):
    #     """
    #     Override the validator to provide additional custom validation based
    #     on our custom logic.
    #     """
    #     step_number = data.get('step_number', 0)
    #     if step_number == 1:
    #         self.validate_step1(data)
    #     elif step_number == 2:
    #         self.validate_step2(data)
    #     elif step_number == 3:
    #         self.validate_step3(data)
    #     elif step_number == 4:
    #         self.validate_step4(data)
    #     elif step_number == 5:
    #         self.validate_step5(data)
    #     elif step_number == 6:
    #         self.validate_step6(data)
    #     else:
    #         raise exceptions.ValidationError({
    #             'step_number': _('Please pick a valid step number.')
    #         })
    #
    #     # Return our data.
    #     return data

    @transaction.atomic
    def create(self, validated_data):
        # Do nothing.
        return validated_data
