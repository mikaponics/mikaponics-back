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

from ecommerce import constants


def get_country_code(country_name):
    try:
        return constants.COUNTRY_CODES[country_name]
    except KeyError:
        return None


def get_country_province_code(country_name, province_name):
    try:
        return constants.COUNTRY_PROVINCE_CODES[country_name][province_name]
    except KeyError:
        return None
