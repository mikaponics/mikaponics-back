# -*- coding: utf-8 -*-
import datetime
from django import template
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse
from foundation import constants


register = template.Library()


@register.simple_tag
def get_app_domain():
    """
    Returns the full URL to the domain. The output from this function gets
    generally appended with a path string.
    """
    url = settings.MIKAPONICS_BACKEND_HTTP_PROTOCOL
    url += settings.MIKAPONICS_BACKEND_HTTP_DOMAIN
    return url
