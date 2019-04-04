# -*- coding: utf-8 -*-
import base64
import hashlib
import string
import re # Regex
from datetime import date, timedelta, datetime, time
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.signing import Signer
from django.core.validators import RegexValidator
from django.db.models import Q
from django.urls import reverse
from django.utils import crypto
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from foundation import constants


def reverse_with_full_domain(reverse_url_id, resolve_url_args=[]):
    url = settings.MIKAPONICS_BACKEND_HTTP_PROTOCOL
    url += settings.MIKAPONICS_BACKEND_HTTP_DOMAIN
    url += reverse(reverse_url_id, args=resolve_url_args)
    url = url.replace("None","en")
    return url


def pretty_dt_string(dt):  #TODO: UNIT TEST
    """
    Utility function will convert the naive/aware datatime to a pretty datetime
    format which will work well for output.
    """
    if dt is None:
        return None

    try:
        dt = dt.replace(microsecond=0)
        dt = dt.replace(second=0)
        dt_string = dt.strftime("%m-%d-%Y %H:%M:%S")
    except Exception as e:
        dt_string = dt.strftime("%m-%d-%Y")
    return dt_string


def generate_hash(value=None):
    """
    TODO: UNIT TEST
    """
    # Handle null values.
    if value is None or value == '':
        value = timezone.now()
        value = value.timestamp()

    # Convert whatever data format into a string value.
    value_str = str(value)

    # Conver into UTF-8 formatted string value
    utf8_value_str = value_str.encode('utf8', 'ignore')

    # Return the hash binary data.
    byte_data = base64.urlsafe_b64encode(hashlib.sha256(utf8_value_str).digest())

    # Convert to a UTF-8 string.
    return byte_data.decode("utf-8")


def get_random_string(length=31,
                      allowed_chars='abcdefghijkmnpqrstuvwxyz'
                      'ABCDEFGHIJKLMNPQRSTUVWXYZ'
                      '23456789'):
    """
    Random string generator simplified from Django.

    TODO: UNIT TEST
    """
    return crypto.get_random_string(length, allowed_chars)


def get_unique_username_from_email(email):
    """
    Return a hash, which will fit into django "username" field of the `User`
    object, of the email.

    TODO: UNIT TEST
    """
    email = email.lower()  # Emails should be case-insensitive unique
    hashed_email = generate_hash(email)
    return hashed_email[:30]




def int_or_none(value):
    """
    TODO: UNIT TEST
    """
    try:
        return int(value)
    except Exception as e:
        return None


def float_or_none(value):
    """
    TODO: UNIT TEST
    """
    try:
        return float(value)
    except Exception as e:
        return None


def get_country_province_code(country_name, province_name):
    try:
        return constants.COUNTRY_PROVINCE_CODES[country_name][province_name]
    except KeyError:
        return None
